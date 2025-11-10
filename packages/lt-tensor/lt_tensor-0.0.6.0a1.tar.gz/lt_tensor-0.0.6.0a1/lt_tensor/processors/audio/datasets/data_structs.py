__all__ = ["AudioData", "CollateProcessor"]
from lt_utils.common import *
import torch
from torch import Tensor, LongTensor
from torch.nn import functional as F
from lt_tensor.masking_utils import length_to_mask


class AudioData:
    text: Optional[str] = None
    text_file: Optional[str] = None

    def __init__(
        self,
        wave: Tensor,
        duration: float,
        sample_rate: float,
        speaker_id: str,
        audio_path: Optional[str] = None,
        noise_reduction: float = 0.0,
        vad: bool = False,
        speech_id: int = -1,
        top_db: Optional[float] = None,
        text_path: Optional[str] = None,
        text: Optional[str] = None,
        text_file_postfix: str = "",
        reference: Optional[Tensor] = None,
        *args,
        **kwargs,
    ):
        self.wave = wave
        self.wave_length = wave.size(-1)
        self.duration = duration
        self.sample_rate = sample_rate
        self.audio_path = audio_path
        self.text_path = text_path
        self.vad = vad
        self.top_db = top_db
        self.noise_reduction = noise_reduction
        self.text_file_postfix = text_file_postfix
        self.speaker_id = speaker_id
        self.speech_id = max(int(speech_id), -1)
        self.reference = reference
        if text:
            self.text = text
        if text_path:
            self.text_file = Path(text_path).name

    def save_text(
        self,
        text_file_postfix: str = ".processed",
        replace_contents: bool = False,
    ):
        """Useful when using with processors."""
        if self.text is None or self.text_path is None or self.text_file is None:
            return False
        if not replace_contents and text_file_postfix == self.text_file_postfix:
            return False
        new_name = self.text_file.replace(self.text_file_postfix, text_file_postfix)
        new_name = new_name.replace("..", ".")
        path = Path(self.text_path).parent / new_name
        path.write_bytes(self.text.encode())
        return True

    def get_duration(self):
        return self.wave.size(-1) / self.sample_rate

    def get_duration_as_tensor(self):
        return torch.as_tensor(self.get_duration())

    def _cbrt_check_text(
        self,
        text: Optional[str],
        text_required: bool = False,
        should_be_equal: Optional[bool] = None,
    ):
        if self.text is None or text is None:
            return not text_required

        if should_be_equal is None:
            # we dont check
            return True

        if should_be_equal:
            return text == self.text

        return text != self.text

    def can_be_reference_to(
        self,
        speaker_id: str,
        speech_id: int = -1,
        text: Optional[str] = None,
        text_required: bool = False,
        should_text_be_equal: Optional[bool] = None,
        should_speaker_be_equal: Optional[bool] = None,
        can_share_same_id: bool = False,
    ):
        """Used to get the same speaker or different speaker to train voice changers or TTS that uses voice-cloning features."""
        are_speakers_equal = speaker_id == self.speaker_id

        if should_speaker_be_equal is not None:
            if should_speaker_be_equal:
                if not are_speakers_equal:
                    return False
            else:
                if are_speakers_equal:
                    return False

        if not self._cbrt_check_text(text, text_required, should_text_be_equal):
            return False

        if not are_speakers_equal:
            # no reason to investigate further in this case.
            return True

        if can_share_same_id or self.speech_id == -1 or speech_id == -1:
            # case true we dont need to check.
            return True

        return speech_id != self.speaker_id

    def can_be_reference_to_other(
        self,
        other: "AudioData",
        text_required: bool = False,
        should_text_be_equal: Optional[bool] = None,
        should_speaker_be_equal: Optional[bool] = None,
        can_share_same_id: bool = False,
    ):
        return self.can_be_reference_to(
            other.speaker_id,
            other.speech_id,
            other.text,
            text_required,
            should_text_be_equal,
            should_speaker_be_equal,
            can_share_same_id,
        )


_COMP_Q_SAMPLE_TP: TypeAlias = Callable[
    [Tensor, Tensor, Union[int, Tensor]],
    Tuple[Tensor, Tensor, Tensor],
]


class DiffusionOutputs(OrderedDict):

    @property
    def xt(self) -> Tensor:
        return self.get("xt")

    @property
    def eps(self) -> Tensor:
        return self.get("eps")

    @property
    def t(self) -> Tensor:
        return self.get("t")

    def __init__(
        self,
        xt: Tensor,
        eps: Tensor,
        t: Tensor,
    ):
        super().__init__({"xt": xt, "eps": eps, "t": t})
        self.inp_size = xt.shape[-1]
        self.batch_size = xt.shape[0]


class InputIDsData(OrderedDict):
    inp_size: int = 0

    @property
    def input_ids(self) -> LongTensor:
        return self.get("input_ids")

    @property
    def lengths(self) -> List[int]:
        return self.get("lengths")

    @property
    def mask(self) -> Tensor:
        return self.get("mask")

    def get_attn_mask(self, n_heads: int = 1) -> Tensor:
        """scaled_dot_product_attention"""
        return self.mask.reshape(self.batch_size, 1, 1, self.inp_size).expand(
            -1, n_heads, self.inp_size, -1
        )

    def __init__(
        self,
        input_ids: Tensor,
        lengths: List[int],
        mask: Tensor,
    ):
        super().__init__({"input_ids": input_ids, "lengths": lengths, "mask": mask})
        self.inp_size = input_ids.shape[-1]
        self.batch_size = input_ids.shape[0]


class CollateProcessor:
    largest_wave: int = 0
    largest_mel: int = 0
    largest_text: int = 0
    largest_reference: int = 0
    device = torch.device("cpu")

    def __init__(
        self,
        wave: List[Tensor],
        pad_id: int,
        compute_mel_fn: Callable[[Tensor], Tensor],
        compute_mel_fn2: Callable[[Tensor], Tensor],
        scheduler_q_sample_fn: _COMP_Q_SAMPLE_TP,
        input_ids: Optional[List[LongTensor]] = None,
        reference: Optional[List[Tensor]] = None,
        device: Optional[Union[str, torch.device]] = None,
    ):
        if device is not None:
            self.to(device)
        self.batch_size = len(wave)
        self.pad_id = pad_id
        self._wave = wave
        self._mel = [compute_mel_fn(x) for x in self._wave]
        self._input_ids = input_ids
        self.n_mels = self._mel[0].size(-2)

        self.compute_mel_fn: Callable[[Tensor], Tensor] = compute_mel_fn
        self.compute_mel_fn2: Callable[[Tensor], Tensor] = compute_mel_fn2
        self.scheduler_q_sample_fn: _COMP_Q_SAMPLE_TP = scheduler_q_sample_fn
        if self._input_ids is not None:
            self.largest_text = max(self.lengths)
        self.largest_wave = int(self.durations_wave.max().item())
        self.largest_mel = int(self.durations.max().item())
        self.reference = reference

        if self.reference is not None:
            self.largest_reference = max([x.size(-1) for x in self.reference])

    def to(self, device: Union[str, torch.device]):
        if isinstance(device, torch.device):
            self.device = device
        else:
            self.device = torch.device(device)

    @property
    def wave(self):
        return (
            torch.stack(
                [
                    F.pad(x, (0, self.largest_wave - x.size(-1))).squeeze()
                    for x in self._wave
                ]
            )
            .view(self.batch_size, 1, -1)
            .to(self.device)
        )

    @property
    def mel(self):
        return (
            torch.stack(
                [
                    F.pad(x, (0, self.largest_mel - x.size(-1))).squeeze()
                    for x in self._mel
                ]
            )
            .view(self.batch_size, self.n_mels, -1)
            .to(self.device)
        )

    @property
    def mel2(self):
        mels = [self.compute_mel_fn2(x) for x in self._wave]
        return (
            torch.stack(
                [F.pad(x, (0, self.largest_mel - x.size(-1))).squeeze() for x in mels]
            )
            .view(self.batch_size, self.n_mels, -1)
            .to(self.device)
        )

    @property
    def durations(self):
        return torch.as_tensor(
            [x.size(-1) for x in self._mel],
            dtype=torch.float,
            device=self.device,
        )

    @property
    def durations_wave(self):
        return torch.as_tensor(
            [x.size(-1) for x in self._wave],
            dtype=torch.float,
            device=self.device,
        )

    @property
    def input_ids(self):
        if self._input_ids is None:
            return None
        return (
            torch.stack(
                [
                    F.pad(x, (0, self.largest_text - x.size(-1)), value=self.pad_id)
                    for x in self._input_ids
                ]
            )
            .view(self.batch_size, -1)
            .long()
            .to(self.device)
        )

    @property
    def lengths(self):
        if self._input_ids is None:
            return None
        return [x.size(-1) for x in self._input_ids]

    @property
    def lengths_mask(self):
        if self._input_ids is None:
            return None
        return length_to_mask(self.lengths, 1).to(self.device)

    @property
    def mask(self):
        if self._input_ids is None:
            return None
        return self.input_ids.eq(self.pad_id)

    @property
    def mel_lengths(self):
        return [x.size(-1) for x in self._mel]

    @property
    def wave_lengths(self):
        return [x.size(-1) for x in self._wave]

    def get_input_ids(self, *_, **__) -> Optional[InputIDsData]:
        if self._input_ids is None:
            return None

        lengths = self.lengths
        input_ids = self.input_ids

        return InputIDsData(
            input_ids=input_ids,
            lengths=lengths,
            mask=input_ids.eq(self.pad_id),
        )

    def get_diffusion_wave(
        self,
        t: Optional[Union[Tensor, int]] = None,
        noise: Optional[Tensor] = None,
        *args,
        **kwargs,
    ) -> DiffusionOutputs:
        l_xt: List[Tensor] = []
        l_eps: List[Tensor] = []
        l_t: List[Tensor] = []
        for wave in self._wave:
            xt, eps, _t = self.scheduler_q_sample_fn(wave, noise, t)

            pad = self.largest_wave - eps.size(-1)
            l_xt.append(F.pad(xt, (0, pad)).squeeze())
            l_t.append(_t)
            l_eps.append(F.pad(eps, (0, pad)).squeeze())

        # outputs
        xt_out = torch.stack(l_xt).view(self.batch_size, 1, -1).to(self.device)
        eps_out = torch.stack(l_eps).view_as(xt_out).to(self.device)
        t_out = torch.stack(l_t).view(self.batch_size, -1).to(self.device)

        return DiffusionOutputs(
            xt=xt_out,
            eps=eps_out,
            t=t_out,
        )

    def get_diffusion_mel(
        self,
        t: Optional[Union[Tensor, int]] = None,
        noise: Optional[Tensor] = None,
        per_wave: bool = False,
        mel_fn_id: Literal["1", "2"] = "2",
    ) -> DiffusionOutputs:
        """
        Args:
            per_wave (bool, optional): makes the noising process over the wave before converting to mel,
                                        instead of noising the mel spectrograms, not recommended for traditional training.
                                        Experimental and unsafe to use. Defaults to False.

        """
        mel_fn_id = str(mel_fn_id)
        assert mel_fn_id in ["1", "2"], "Choose either id 1 or id 2 for `mel_fn_id`"
        if per_wave:
            return self._get_diffusion_mel2(t=t, mel_fn_id=mel_fn_id, noise=noise)
        return self._get_diffusion_mel1(t=t, mel_fn_id=mel_fn_id, noise=noise)

    def get_wave_reference(self):
        assert self.reference, "Reference not available!"
        return torch.stack(
            [
                F.pad(x, (0, self.largest_reference - x.size(-1))).squeeze()
                for x in self.reference
            ],
            dim=0,
        ).to(self.device)

    def get_mel_reference(
        self,
        mel_fn_id: Literal["1", "2"] = "2",
    ):
        assert self.reference, "Reference not available!"
        mel_fn_id = str(mel_fn_id)
        assert mel_fn_id in ["1", "2"], "Choose either id 1 or id 2 for `mel_fn_id`"

        mel_fn = self.compute_mel_fn2 if mel_fn_id == "2" else self.compute_mel_fn
        mels = [mel_fn(x) for x in self.reference]
        largest = max([mel.size(-1) for mel in mels])
        return torch.stack(
            [F.pad(x, (0, largest - x.size(-1))).squeeze() for x in mels],
            dim=0,
        ).to(self.device)

    def _get_diffusion_mel1(
        self,
        t: Optional[Union[Tensor, int]] = None,
        noise: Optional[Tensor] = None,
        mel_fn_id: Literal["1", "2"] = "2",
    ):
        """Similar to 'get_diffusion', but here we target the mel-spec instead"""
        mel_fn_id = str(mel_fn_id)
        assert mel_fn_id in ["1", "2"], "Choose either id 1 or id 2 for `mel_fn_id`"

        l_xt: List[Tensor] = []
        l_eps: List[Tensor] = []
        l_t: List[Tensor] = []
        if mel_fn_id == "1":
            _mels = self.mel
        else:
            _mels = [self.compute_mel_fn2(x) for x in self._wave]

        for mel in _mels:
            xt, eps, _t = self.scheduler_q_sample_fn(mel, noise, t)

            l_xt.append(F.pad(xt, (0, self.largest_mel - xt.size(-1))).squeeze())
            l_eps.append(F.pad(eps, (0, self.largest_mel - eps.size(-1))).squeeze())
            l_t.append(_t)

        # outputs
        xt_out = torch.stack(l_xt).to(self.device)
        eps_out = torch.stack(l_eps).to(self.device)
        t_out = torch.stack(l_t).view(self.batch_size, -1).to(self.device)

        return DiffusionOutputs(
            xt=xt_out,
            eps=eps_out,
            t=t_out,
        )

    def _get_diffusion_mel2(
        self,
        t: Optional[Union[Tensor, int]] = None,
        noise: Optional[Tensor] = None,
        mel_fn_id: Literal["1", "2"] = "2",
    ):
        """Similar to '_get_diffusion_mel1', but here we add noise into the wave
        then use a mel spectrogram in each output to get the value, instead of the opposite
        """
        mel_fn_id = str(mel_fn_id)
        assert mel_fn_id in ["1", "2"], "Choose either id 1 or id 2 for `mel_fn_id`"

        l_xt: List[Tensor] = []
        l_eps: List[Tensor] = []
        l_t: List[Tensor] = []
        _waves = [self.scheduler_q_sample_fn(x, noise, t) for x in self._wave]
        mel_fn = self.compute_mel_fn if mel_fn_id == "1" else self.compute_mel_fn2

        for xt, eps, timesteps in _waves:
            xt_mel = mel_fn(xt)
            eps_mel = mel_fn(eps)

            l_xt.append(
                F.pad(xt_mel, (0, self.largest_mel - xt_mel.size(-1))).squeeze()
            )
            l_eps.append(
                F.pad(eps_mel, (0, self.largest_mel - eps_mel.size(-1))).squeeze()
            )
            l_t.append(timesteps)

        # outputs
        xt_out = torch.stack(l_xt).to(self.device)
        eps_out = torch.stack(l_eps).to(self.device)
        t_out = torch.stack(l_t).view(self.batch_size, -1).to(self.device)

        return DiffusionOutputs(
            xt=xt_out,
            eps=eps_out,
            t=t_out,
        )
