__all__ = [
    "mel_to_hz",
    "hz_to_mel",
    "power_to_db",
    "mel_filterbank",
    "mel_frequencies",
    "amplitude_to_db",
    "tempo_frequencies",
    "fourier_tempo_frequencies",
]
import numpy as np
from lt_utils.common import *
from lt_tensor.common import *
import warnings
from lt_tensor.tensor_ops import sub_outer


def mel_to_hz(
    mels: Tensor,
    *,
    htk: bool = False,
    dtype: Optional[Union[torch.device, str]] = torch.float64,
) -> Tensor:
    """Adapted from librosa"""
    if htk:
        return 700.0 * (10.0 ** (mels / 2595.0) - 1.0)

    # Fill in the linear scale
    f_min = 0.0
    f_sp = 200.0 / 3
    freqs = f_min + f_sp * mels

    # And now the nonlinear scale
    min_log_hz = 1000.0  # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp  # same (Mels)
    logstep = (
        torch.log(torch.as_tensor(6.4, dtype=dtype)) / 27.0
    )  # step size for log region

    if mels.ndim:
        # If we have vector data, vectorize
        log_t = mels >= min_log_mel
        freqs[log_t] = min_log_hz * torch.exp(logstep * (mels[log_t] - min_log_mel))
    elif mels >= min_log_mel:
        # If we have scalar data, check directly
        freqs = min_log_hz * torch.exp(logstep * (mels - min_log_mel))

    return freqs


def hz_to_mel(
    frequencies: float,
    *,
    htk: bool = False,
    dtype: Optional[Union[torch.device, str]] = torch.float64,
) -> torch.Tensor:
    """Adapted from librosa"""
    frequencies = torch.as_tensor(frequencies)

    if htk:
        mels = 2595.0 * torch.log10(1.0 + frequencies / 700.0)
        return mels

    # Fill in the linear part
    f_min = 0.0
    f_sp = 200.0 / 3

    mels = (frequencies - f_min) / f_sp

    # Fill in the log-scale part

    min_log_hz = 1000.0  # beginning of log region (Hz)
    min_log_mel = (min_log_hz - f_min) / f_sp  # same (Mels)
    logstep = (
        torch.log(torch.as_tensor(6.4, dtype=dtype)) / 27.0
    )  # step size for log region

    if frequencies.ndim:
        # If we have array data, vectorize
        log_t = frequencies >= min_log_hz
        mels[log_t] = min_log_mel + torch.log(frequencies[log_t] / min_log_hz) / logstep
    elif frequencies >= min_log_hz:
        # If we have scalar data, heck directly
        mels = min_log_mel + torch.log(frequencies / min_log_hz) / logstep

    return mels


def mel_frequencies(
    n_mels: int = 128,
    *,
    f_min: float = 0.0,
    f_max: float = 11025.0,
    htk: bool = False,
    dtype: Optional[Union[torch.device, str]] = torch.float64,
):
    """Adapted from librosa"""
    min_mel = hz_to_mel(f_min, htk=htk, dtype=dtype)
    max_mel = hz_to_mel(f_max, htk=htk, dtype=dtype)

    mels = torch.linspace(min_mel, max_mel, n_mels, dtype=dtype)

    hz = mel_to_hz(mels, htk=htk, dtype=dtype)

    return hz


def mel_filterbank(
    sr: float = 24000,
    n_fft: int = 1024,
    n_mels: int = 80,
    f_min: float = 0.0,
    f_max: Optional[float] = None,
    htk: bool = False,
    dtype: Optional[Union[torch.device, str]] = torch.float32,
    device: Optional[torch.device] = None,
):
    """Adapted from librosa"""
    if f_max is None:
        f_max = float(sr) / 2

    # Initialize the weights
    n_mels = int(n_mels)
    weights = torch.zeros((n_mels, int(1 + n_fft // 2)), dtype=dtype)
    fftfreqs = torch.fft.rfftfreq(n=n_fft, d=1.0 / sr, dtype=dtype)
    mel_f = mel_frequencies(n_mels + 2, f_min=f_min, f_max=f_max, htk=htk, dtype=dtype)

    # compare_ramps(mel_f, fftfreqs)
    fdiff = mel_f.diff()
    ramps = sub_outer(mel_f, fftfreqs)
    zero_tensor = torch.zeros(1)
    for i in range(n_mels):
        # lower and upper slopes for all bins
        lower = -ramps[i] / fdiff[i]
        upper = ramps[i + 2] / fdiff[i + 1]
        weights_bd = torch.min(lower, upper)
        # .. then intersect them with each other and zero
        weights[i] = weights_bd.clamp_min(zero_tensor)

    # Slaney-style mel is scaled to be approx constant energy per channel
    enorm = 2.0 / (mel_f[2 : n_mels + 2] - mel_f[:n_mels])
    weights *= enorm[:, torch.newaxis]

    if (weights.max(dim=0).values == 0.0).any().item():
        warnings.warn(
            "At least one mel filterbank has all zero values. "
            f"The value for `n_mels` ({n_mels}) may be set too high. "
            f"Or, the value for `n_fft` ({n_fft}) may be set too low.",
            stacklevel=2,
            category=UserWarning,
        )
    return weights.to(device=device, dtype=dtype)


def amplitude_to_db(
    x: Tensor,
    ref: Union[
        float, Tensor, Literal["min", "max"], Callable[[Tensor], Tensor]
    ] = "max",
    top_db: Optional[float] = None,
    floor_db: Optional[float] = None,
) -> Tensor:
    """
    inspirated in Librosa's `amplitude_to_db` implemented for torch.
    Args:
        x: magnitude or power tensor.
        ref: reference value (scalar or tensor). Default is max.
        top_db: dynamic range limit.
    Returns:
        dB-scaled tensor.
    """
    if torch.is_complex(x):
        x = x.abs()
    if callable(ref):
        ref_value = ref(x)
    elif isinstance(ref, str) and ref.strip():
        if ref == "min":
            ref_value = x.min()
        elif ref == "max":
            ref_value = x.max()
    elif isinstance(ref, (int, float, Tensor, np.ndarray, List)):
        ref_value = torch.as_tensor(ref, dtype=x.dtype, device=x.device)
    else:
        raise ValueError("Invalid ref argument.")

    # numerical stability clamp
    amin = torch.finfo(x.dtype).tiny
    x_db = 20.0 * torch.log10(torch.clamp(x, min=amin)) - 20.0 * torch.log10(
        torch.clamp(ref_value, min=amin)
    )

    # dynamic range compression like librosa
    if top_db is not None:
        max_db = x_db.max()
        x_db = torch.clamp(x_db, min=max_db - top_db)
    if floor_db is not None:
        min_db = x_db.min()
        x_db = torch.clamp(x_db, max=floor_db + min_db)
    return x_db


def tempo_frequencies(
    n_bins: int = 1024,
    sr: float = 24000,
    hop_length: int = 256,
    *,
    nan_to_num: bool = False,
    pos_inf_value: float = 0,
    neg_inf_value: float = 0,
    nan_value: float = 0,
) -> Tensor:
    """Adapted from librosa"""
    bin_frequencies = torch.zeros(int(n_bins), dtype=torch.float64)

    bin_frequencies[0] = torch.inf
    bin_frequencies[1:] = (
        60.0 * sr / (hop_length * torch.arange(1.0, n_bins, dtype=torch.float64))
    )
    if not nan_to_num:
        return bin_frequencies
    return bin_frequencies.nan_to_num(nan_value, pos_inf_value, neg_inf_value)


def fourier_tempo_frequencies(
    *,
    sr: float = 24000,
    win_length: int = 384,
    hop_length: int = 512,
) -> Tensor:
    """Adapted from librosa
    Compute the frequencies (in beats per minute) corresponding
    to a Fourier tempogram matrix.

    """
    # sr / hop_length gets the frame rate
    # multiplying by 60 turns frames / sec into frames / minute
    d = sr * 60 / float(hop_length)
    n = win_length
    return torch.fft.rfftfreq(n=n, d=1.0 / d)


def power_to_db(
    S: Number,
    *,
    ref: Union[float, Callable] = 1.0,
    amin: float = 1e-10,
    top_db: Optional[float] = 80.0,
) -> Tensor:
    """Adapted from librosa
    Convert a power spectrogram (amplitude squared) to decibel (dB) units

    This computes the scaling ``10 * log10(S / ref)`` in a numerically
    stable way.

    """
    if amin <= 0:
        raise ValueError("amin must be strictly positive")

    if top_db is not None:
        if top_db < 0:
            raise ValueError("top_db must be non-negative")

    amin = torch.as_tensor(amin, dtype=torch.float64)

    S = torch.as_tensor(S)

    if torch.is_complex(S):
        magnitude = S.abs()
    else:
        magnitude = S

    if callable(ref):
        # User supplied a function to calculate reference power
        ref_value = ref(magnitude)
    else:
        ref_value = torch.abs(torch.as_tensor(ref, dtype=torch.float64))

    log_spec: Tensor = 10.0 * torch.log10(torch.max(amin, magnitude))
    log_spec -= 10.0 * torch.log10(torch.max(amin, ref_value))
    if top_db is not None:
        log_spec = torch.max(log_spec, log_spec.max() - top_db)

    return log_spec
