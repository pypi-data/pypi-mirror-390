from __future__ import annotations

from lt_tensor.processors.audio.core import AudioProcessor, AudioProcessorConfig
from lt_tensor.training_utils.datasets_templates import DatasetBase
from lt_utils.file_ops import (
    load_text,
    find_dirs,
    find_files,
    get_file_name,
)
from lt_utils.common import *
import numpy as np
from torch import Tensor
from typing import TYPE_CHECKING
import torch
import random
from .utils import *
from .data_structs import *
from typing import Iterable
from contextlib import nullcontext
from torch.nn import functional as F
from typing_extensions import override
from lt_utils.misc_utils import default, get_current_time
from lt_tensor.misc_utils import set_seed
from lt_tensor.noise_tools import NoiseScheduler, DPMSolver, DDPMScheduler
from torchaudio.functional.filtering import vad
from lt_utils.file_ops import load_dataframe, find_files, find_dirs, is_file, is_dir
import pandas as pd

if TYPE_CHECKING:
    from tokenizers import Tokenizer
    from lt_tensor.tokenizer.tokenizer_lt import TokenizerLT


__all__ = ["AudioDatasetWT"]


class AudioDatasetWT(DatasetBase):
    data: pd.DataFrame = []
    chunk_size: int = None
    fixed_size: bool = False
    _bad_files: List[str] = []
    _files_loaded: List[str] = []
    total_duration: float = 0.0
    tokenizer_has_pad: bool = False
    pad_token_id: int = 0
    container_cls = CollateProcessor

    def __init__(
        self,
        ap_config=AudioProcessorConfig(
            sample_rate=24000,
            n_fft=1024,
            hop_length=256,
            win_length=1024,
            n_mels=96,
            f_max=8000,
            mel_power=1.0,
        ),
        ap_config_2=AudioProcessorConfig(  # for labels
            sample_rate=24000,
            n_fft=1024,
            hop_length=256,
            win_length=1024,
            n_mels=96,
            f_max=None,
            mel_power=1.0,
        ),
        tokenizer: Optional[Union["Tokenizer", "TokenizerLT"]] = None,
        pad_token_id: int = 0,
        diffusion_steps: int = 50,
        diff_beta_start: float = 0.0001,
        diff_beta_end: float = 0.05,
        diff_kwargs: dict[str, Any] = {},
        diff_type: Literal["dpm", "ddpm"] = "ddpm",
        *,
        mode: Literal["vocoder", "tts", "style-tts"] = "vocoder",
        duration_per_track: float = 7200,
        chunk_size: int = 8192,
        norm_mel: bool = True,
        norm_wave: bool = True,
        text_processor: Optional[Callable[[str], str]] = None,  # For example phonemizer
        mel_norm_tp: Literal["log_norm", "range_norm"] = "log_norm",
        make_references_optional: bool = False,
        device: Optional[Union[str, torch.device]] = None,
    ):
        super().__init__()
        assert mode in [
            "vocoder",
            "tts",
            "style-tts",
        ], f'Invalid mode {mode}. choose either "tts", "vocoder" or "style-tts"'
        self.ap = AudioProcessor(ap_config)
        self.ap2 = AudioProcessor(ap_config_2)
        self.cfg = ap_config
        self.cfg2 = ap_config_2
        if device is not None:
            torch.randn(1, device=device)
        self.device = device
        self.tokenizer = tokenizer
        self.pad_token_id = pad_token_id
        self.text_processor = text_processor
        self.mel_norm_tp = mel_norm_tp
        self.make_references_optional = make_references_optional
        self.mode: Literal["vocoder", "tts", "style-tts"] = mode
        self.norm_wave = norm_wave
        self.norm_mel = norm_mel
        self.duration_per_track = duration_per_track
        self.chunk_size = max(int(chunk_size), 8)
        # diffusion stuff
        self.diffusion_steps = diffusion_steps
        self.beta_start = diff_beta_start
        if self.chunk_size % 8 != 0:
            self.chunk_size = int(self.chunk_size + self.chunk_size % 8)
        self.diff_type = diff_type
        if diff_type == "dpm":
            self.scheduler = DPMSolver(
                num_train_timesteps=diffusion_steps,
                beta_start=diff_beta_start,
                beta_end=diff_beta_end,
                **diff_kwargs,
            )
        else:
            self.scheduler = DDPMScheduler(
                num_train_timesteps=diffusion_steps,
                beta_start=diff_beta_start,
                beta_end=diff_beta_end,
                **diff_kwargs,
            )

    def load_audio(
        self,
        file: PathLike,
        top_db: Optional[float] = None,
        noise_reduction: float = 0,
        *,
        do_vad: bool = False,
        trigger_time=0.1,
        search_time=0.35,
        allowed_gap=0.25,
        **kwargs,
    ) -> Tensor:
        audio = self.ap.load_audio(
            file,
            top_db=top_db,
            mono=True,
            duration=self.duration_per_track if self.mode == "vocoder" else None,
            normalize=self.norm_wave,
            noise_reduction=noise_reduction,
        ).view(1, -1)
        if do_vad:
            audio = vad(
                audio,
                sample_rate=self.cfg.sample_rate,
                trigger_time=trigger_time,
                search_time=search_time,
                allowed_gap=allowed_gap,
            )
        return audio

    def _try_find_text_file(self, audio_file: str, postfix: str = ""):
        possible_name = (
            get_file_name(audio_file, keep_extension=False) + postfix + ".txt"
        )
        possible_dir = Path(audio_file).parent / possible_name
        return possible_dir, possible_dir.exists()

    def encode_text(
        self,
        text: str,
        pad_size: Optional[int] = None,
    ):
        tokens = torch.as_tensor(self.tokenizer.encode(text))
        if pad_size and tokens.size(-1) < pad_size:
            tokens = F.pad(tokens, (0, pad_size - tokens.size(-1)), value=0)
        return tokens.long()

    def decode_text(self, tokens: Union[Tensor, List[int]]):
        if isinstance(tokens, Tensor):
            tokens = tokens.clone().detach().flatten().long().tolist()
        return self.tokenizer.decode(tokens)

    def get_audio_duration(self, wave: Tensor):
        return wave.size(-1) / self.cfg.sample_rate

    def load_data(
        self,
        path: PathLike,
        min_duration: float = 1.0,
        max_duration: Optional[float] = None,
        min_text_size: int = 1,
        max_text_size: int = int(1e6),
        max_files: int = 999_999,
        *args,
        **kwargs,
    ):
        max_files = int(max(max_files, 1))
        min_text_size = int(max(min_text_size, 1))
        max_text_size = int(max(min_text_size + 1, max_text_size))
        min_duration = max(min_duration, 0.1)
        # stats:
        path = Path(path)
        if is_file(path):
            data = load_dataframe(path)

        elif is_dir(path):
            data = pd.DataFrame()
            for ds_file in find_files(path, ['tts-part-*.parquet"']):
                current = load_dataframe(ds_file)
                data = pd.concat([data, current])
        else:
            return {"total_duration": self.total_duration}
        data: pd.DataFrame = data[
            data["text"].str.len().between(min_text_size, max_text_size)
        ]
        data = data[data["duration"] >= min_duration]
        if max_duration is not None:
            data = data[data["duration"] <= max_duration]
        if not isinstance(self.data, pd.DataFrame):
            self.data = data
        else:
            self.data = pd.concat([self.data, data])
        self.data.drop_duplicates(subset=["audio"], keep="last")
        self.data["processed_text"] = self.data["processed_text"].fillna(
            self.data["text"]
        )

        self.total_duration = self.data["duration"].sum().item()
        return {"total_duration": self.total_duration}

    def compute_mel(self, wave: Tensor) -> Tensor:
        B = 1 if wave.ndim < 2 else wave.size(0)
        return self.ap.compute_mel(
            wave,
            norm=self.norm_mel,
            norm_type=self.mel_norm_tp,
        ).view(B, self.cfg.n_mels, -1)

    def compute_mel2(self, wave: Tensor) -> Tensor:
        B = 1 if wave.ndim < 2 else wave.size(0)
        return self.ap2.compute_mel(
            wave,
            norm=self.norm_mel,
            norm_type=self.mel_norm_tp,
        ).view(B, self.cfg.n_mels, -1)

    @override
    def sample(self, seed: Optional[int] = None, *args, **kwargs):
        total = len(self)
        if not total:
            raise RuntimeError("The dataset is empty!")
        if seed is not None:
            set_seed(seed)
        data = self.data.sample(1)
        if self.mode != "vocoder":
            return data
        return self.ap.audio_splitter(
            self.load_audio(data["audio"]), chunk_size=self.chunk_size
        )

    def samples(
        self,
        number: int = 1,
        seed: Optional[int] = None,
        show_progress: bool = False,
        randomized: bool = False,
        *args,
        **kwargs,
    ):
        total = len(self)
        if not total:
            raise RuntimeError("The dataset is empty!")
        number = int(max(number, 1))

        if total < number:
            number = total
        items_ids: List[int] = torch.arange(0, total).tolist()
        if not randomized:
            item_ids = items_ids[:number]
        else:
            if seed is not None:
                set_seed(seed)
            item_ids = random.sample(items_ids, k=number)
        if self.mode != "vocoder":
            return [self.__getitem__(i) for i in item_ids]

        fragmented = []
        if show_progress:
            from tqdm import tqdm

            progress = tqdm(items_ids, "Processing data")
        else:
            progress = items_ids

        for i in progress:
            fragmented.extend(
                self.ap.audio_splitter(
                    self.__getitem__[i].wave, chunk_size=self.chunk_size
                )
            )
        return fragmented

    def _find_reference_to(self, target: AudioData):
        seq = torch.arange(0, len(self.data), 1).flatten().tolist()
        random.shuffle(seq)
        for i in seq:
            if target.can_be_reference_to_other(
                self.data[i],
                text_required=False,
                should_speaker_be_equal=self.mode == "style-tts",
                can_share_same_id=True,
            ):
                return self.data[i].wave
        if not self.make_references_optional:
            raise ValueError("Reference not found")
        return torch.randn(1, self.cfg.sample_rate * random.uniform(0.5, 2))

    @override
    def collate_fn(self, batch: Sequence[AudioData]):
        reference = None
        input_ids = None
        if "tts" in self.mode:
            input_ids = [self.encode_text(x.text) for x in batch]
            if self.mode == "style-tts":
                reference = [x.reference for x in batch]
            wave = [x.wave for x in batch]
        elif self.mode == "vocoder":
            wave = [
                self.ap.random_segment(x.wave, chunk_size=self.chunk_size)
                for x in batch
            ]
        return CollateProcessor(
            wave=wave,
            compute_mel_fn=self.compute_mel,
            compute_mel_fn2=self.compute_mel2,
            scheduler_q_sample_fn=self.scheduler.add_noise,
            input_ids=input_ids,
            reference=reference,
            device=self.device,
            pad_id=self.pad_token_id,
        )

    @override
    def _dataset_samples(
        self,
        number: int = 1,
        auto_adjust: bool = False,
        seed: Optional[int] = None,
        randomized: bool = True,
        *args,
        **kwargs,
    ):
        total = len(self)
        if not total:
            raise RuntimeError("The dataset is empty!")
        number = int(max(number, 1))

        if total < number:
            if not auto_adjust:
                raise RuntimeError(
                    f"The dataset does not contain {number} of items available. It only has {len(self.data)}."
                )
            number = total
        items_ids: List[int] = self.data.index.tolist()
        if not randomized:
            item_ids = items_ids[:number]
        else:
            if seed is not None:
                set_seed(seed)
            item_ids = random.sample(items_ids, k=number)
        return [self.__getitem__(i) for i in item_ids]

    @override
    def get_dataloader(
        self,
        train_batch_size: int = 1,
        eval_batch_size: int = 1,
        train_shuffle: bool = True,
        eval_shuffle: bool = False,
        eval_ratio: float = 0.0,
        seed: Optional[int] = None,
        total_items: Optional[int] = None,
        num_workers: int = 0,
        **kwargs,
    ) -> Tuple[
        Iterable[CollateProcessor],
        Optional[Iterable[CollateProcessor]],
    ]:
        return super().get_dataloader(
            train_batch_size=train_batch_size,
            eval_batch_size=eval_batch_size,
            train_shuffle=train_shuffle,
            eval_shuffle=eval_shuffle,
            eval_ratio=eval_ratio,
            seed=seed,
            total_items=total_items,
            num_workers=num_workers,
            collate_fn=self.collate_fn,
        )

    def __getitem__(self, index: int):
        wave_idx = self.data["audio"][index]
        if not isinstance(wave_idx, (Tensor, np.ndarray)):
            wave = self.load_audio(self.data["audio"][index])
        else:
            wave = torch.as_tensor(wave_idx).view(1, -1)
        ref = None
        speaker_id = self.data["speaker_id"][index]

        if self.mode == "style-tts":
            possibilities: pd.DataFrame = self.data[
                self.data["speaker_id"] == speaker_id
            ]
            if len(possibilities) == 1:
                ref = wave.clone()
            else:
                choice = random.choice(list(possibilities.to_dict()["audio"].values()))
                ref = self.load_audio(choice)
        return AudioData(
            wave=wave,
            duration=self.get_audio_duration(wave),
            speaker_id=speaker_id,
            text=self.data["processed_text"][index],
            reference=ref,
            sample_rate=self.cfg.sample_rate,
        )
