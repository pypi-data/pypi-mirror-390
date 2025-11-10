__all__ = ["convert_to_16_bits", "array_to_bytes"]
from lt_utils.common import *
from lt_tensor.common import *
import numpy as np
import wave
import io


def convert_to_16_bits(
    audio: Tensor,
    max_norm: bool = False,
    out_mode: Literal["default", "half", "short"] = "default",
):
    """Convert and audio from float32 to float16"""
    if audio.dtype in [torch.float16, torch.bfloat16]:
        return audio
    if max_norm:
        data = audio / audio.abs().max()
    else:
        data = audio
    data = data * 32767
    if out_mode == "short":
        return data.short()
    elif out_mode == "half":
        return data.half()
    return data


def array_to_bytes(audio_array: Union[Tensor, np.ndarray], sample_rate: int = 24000):

    audio_array = np.asarray(audio_array)
    byte_io = io.BytesIO()
    with wave.open(byte_io, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono audio
        wav_file.setsampwidth(2)  # 16-bit audio
        wav_file.setframerate(sample_rate)
        wav_file.writeframes((audio_array * 32767).astype(np.int16).tobytes())
    return byte_io.getvalue()
