from __future__ import annotations

__all__ = ["find_load_validate_audios"]
from lt_tensor.processors.audio.core import AudioProcessor
from lt_utils.file_ops import (
    load_text,
    find_dirs,
    get_file_name,
    is_pathlike,
    is_file,
)
from lt_utils.common import *
from contextlib import nullcontext
from .data_structs import AudioData
from torchaudio.functional.filtering import vad
import numpy as np
from lt_utils.file_ops import is_pathlike, path_to_str
from lt_utils.misc_utils import filter_kwargs
from uuid import uuid4


def _find_text_file(audio_file: str, postfix: str = ""):
    possible_name = get_file_name(audio_file, keep_extension=False) + postfix + ".txt"
    possible_dir = Path(audio_file).parent / possible_name
    return path_to_str(possible_dir), possible_dir.exists()


def find_load_validate_audios(
    ap: AudioProcessor,
    root_dir: Union[PathLike, List[PathLike]],
    black_list: List[str] = [],
    min_time: Optional[float] = None,
    max_time: Optional[float] = None,
    max_audios: int = int(1e7),
    min_audios_per_dir: int = 2,
    max_audios_per_dir: int = int(1e5),
    normalize: bool = True,
    top_db: Optional[float] = None,
    noise_reduction: float = 0,
    mono: bool = True,
    show_progress: bool = True,
    search_text_file: bool = False,
    requires_text_file: bool = False,
    text_file_postfix: str = ".original",
    text_encoding: Optional[
        Union[str, Literal["utf-8", "ascii", "unicode-escape", "latin-1"]]
    ] = "utf-8",
    text_errors: Union[str, Literal["strict", "ignore"]] = "ignore",
    do_vad: bool = False,
    same_speaker_id: bool = False,
    vad_kwargs: Dict[str, Any] = {},
) -> List[AudioData]:
    results: List[AudioData] = []

    min_audios_per_dir = int(
        max(min_audios_per_dir, 2)
    )  # we need 1 audio and 1 ref at least
    max_audios_per_dir = max(int(max_audios_per_dir), min_audios_per_dir + 1)

    # sample rate
    sample_rate = ap.cfg.sample_rate

    # min frames
    _min_frames = ap.cfg.n_fft * 2
    _clamp_min_time = _min_frames / sample_rate
    found_dirs = []
    if is_pathlike(root_dir, True):
        found_dirs = find_dirs(root_dir, deep=False)
    elif isinstance(root_dir, (list, tuple)) and root_dir:
        for d in root_dir:

            if not is_pathlike(d) or not Path(d).exists():
                continue
            if is_file(d):
                parent = str(Path(d).parent)
                if parent not in found_dirs:
                    found_dirs.append(parent)
            else:
                if str(d) not in found_dirs:
                    found_dirs.append(d)

    if min_time is None or min_time < _clamp_min_time:
        min_time = _clamp_min_time

    if show_progress:
        from tqdm import tqdm

        progress = tqdm(
            range(len(found_dirs)),
            "loading audio data",
            total=max_audios,
        )
    else:
        progress = nullcontext()
    real_estimative = []
    if same_speaker_id:
        current_id = uuid4().hex
        current_set_id = 0
    if vad_kwargs:
        vad_kwargs = filter_kwargs(
            vad, False, ["waveform", "input", "wave", "sr", "sample_rate"], **vad_kwargs
        )
    vad_kwargs.setdefault("trigger_time", 0.1)
    vad_kwargs.setdefault("search_time", 0.25)
    vad_kwargs.setdefault("allowed_gap", 0.25)
    with progress:
        for d in found_dirs:
            if len(results) >= max_audios:
                break
            found = [x for x in ap.find_audios(d) if x not in black_list]
            if show_progress:
                real_estimative.append(len(found))
                progress.total = min(
                    np.mean(real_estimative).item().__ceil__() * len(found_dirs),
                    max_audios,
                )
            if len(found) < min_audios_per_dir:
                continue
            current_set = 0
            if not same_speaker_id:
                current_set_id = 0
                current_id = uuid4().hex
            for audio in found:
                text_path = None
                text = None
                if search_text_file:
                    text_path, text_found = _find_text_file(
                        audio, postfix=text_file_postfix
                    )
                    if not text_found:
                        if requires_text_file:
                            continue
                    else:
                        text = load_text(
                            text_path, encoding=text_encoding, errors=text_errors
                        )
                wave = ap.load_audio(
                    audio,
                    normalize=normalize,
                    top_db=top_db,
                    duration=max_time,
                    mono=mono,
                    noise_reduction=noise_reduction,
                )
                if do_vad:
                    wave = vad(
                        wave,
                        sample_rate=sample_rate,
                        trigger_time=0.1,
                        search_time=0.35,
                        allowed_gap=0.25,
                    )
                wave_dur = wave.size(-1) / sample_rate
                if wave_dur < min_time:
                    continue
                results.append(
                    AudioData(
                        wave=wave,
                        sample_rate=sample_rate,
                        audio_path=audio,
                        duration=wave_dur,
                        text_path=text_path,
                        speaker_id=current_id,
                        speech_id=current_set_id,
                        text=text,
                        noise_reduction=noise_reduction,
                        vad=do_vad,
                        text_file_postfix=text_file_postfix,
                    )
                )
                if show_progress:
                    progress.update()
                if len(results) >= max_audios:
                    break
                current_set += 1
                current_set_id += 1
                if current_set >= max_audios_per_dir:
                    break
    return results
