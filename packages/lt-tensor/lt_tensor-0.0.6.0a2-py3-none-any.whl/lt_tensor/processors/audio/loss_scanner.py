__all__ = ["LossScannerSTFT", "LossScannerMel"]

import torch
import optuna
import warnings
from lt_utils.common import *
from lt_tensor.common import *
from lt_tensor.processors.audio.losses import (
    SingleResolutionMelLoss,
    SingleResolutionSTFTLoss,
)
from abc import ABC, abstractmethod

from lt_tensor.training_utils.losses.scanner import LossScanner


class LossScannerSTFT(LossScanner):
    def __init__(
        self,
        sample_rate: int = 24000,
        min_n_fft: int = 8,
        max_n_fft: int = 2048,
        min_hop: int = 4,
        max_hop: int = 1024,
        hop_step: int = 16,
        n_fft_step: int = 32,
        *,
        trials: int = 128,
        show_progress_bar: bool = True,
        study_direction: Literal["maximize", "minimize"] = "maximize",
        **kwargs
    ):
        super().__init__(
            trials=trials,
            show_progress_bar=show_progress_bar,
            study_direction=study_direction,
            **kwargs
        )
        self.min_n_fft = min_n_fft
        self.max_n_fft = max_n_fft
        self.min_hop = min_hop
        self.max_hop = max_hop
        self.hop_step = hop_step
        self.n_fft_step = n_fft_step
        self.sample_rate = sample_rate

    @torch.no_grad()
    def objective(
        self,
        trial: optuna.trial.Trial,
        real_audio: Tensor,
        fake_audio: Tensor,
    ):
        n_fft = trial.suggest_int(
            "n_fft", self.min_n_fft, self.max_n_fft, step=self.n_fft_step
        )
        hop_length = trial.suggest_int(
            "hop_length", self.min_hop, self.max_hop, step=self.hop_step
        )
        window = trial.suggest_categorical(
            "window",
            ["hann", "hamming", "blackman", "kaiser"],
        )
        with warnings.catch_warnings():
            warnings.filterwarnings(action="ignore", category=UserWarning)
            try:
                loss_fn = SingleResolutionSTFTLoss(
                    window=window,
                    n_fft=n_fft,
                    hop_length=hop_length,
                ).cpu()

                loss_val = loss_fn(fake_audio.cpu(), real_audio.cpu()).item()
                return loss_val

            except Exception:
                return -1e5


class LossScannerMel(LossScanner):
    def __init__(
        self,
        sample_rate: int = 24000,
        min_n_fft: int = 32,
        max_n_fft: int = 2048,
        min_n_mels: int = 32,
        max_n_mels: int = 320,
        mels_step: int = 16,
        n_fft_step: int = 32,
        hop_distance: Number = 4,
        *,
        trials: int = 128,
        show_progress_bar: bool = True,
        study_direction: Literal["maximize", "minimize"] = "maximize",
        **kwargs
    ):
        super().__init__(
            trials=trials,
            show_progress_bar=show_progress_bar,
            study_direction=study_direction,
            **kwargs
        )
        self.min_n_fft = min_n_fft
        self.max_n_fft = max_n_fft
        self.min_n_mels = min_n_mels
        self.max_n_mels = max_n_mels
        self.mels_step = mels_step
        self.n_fft_step = n_fft_step
        self.hop_distance = hop_distance
        self.sample_rate = sample_rate

    @torch.no_grad()
    def objective(
        self,
        trial: optuna.trial.Trial,
        inputs: Tensor,
        labels: Tensor,
    ):
        n_mels = trial.suggest_int(
            "n_mels", self.min_n_mels, self.max_n_mels, step=self.mels_step
        )
        n_fft = trial.suggest_int(
            "n_fft", self.min_n_fft, self.max_n_fft, step=self.n_fft_step
        )
        window = trial.suggest_categorical(
            "window",
            [
                "hann",
                "hamming",
                "blackman",
                "kaiser",
            ],
        )
        hop_length = int(n_fft / self.hop_distance)
        with warnings.catch_warnings():
            warnings.filterwarnings(action="ignore", category=UserWarning)
            try:
                loss_fn = SingleResolutionMelLoss(
                    n_mels=n_mels,
                    n_fft=n_fft,
                    window_length=n_fft,
                    hop_length=hop_length,
                    window=window,
                ).cpu()

                fb = getattr(loss_fn.mel_fn.mel_scale, "fb", None)
                if fb is not None and (fb.max(dim=0).values == 0.0).any():
                    return -1e5

                loss_val = loss_fn(labels.cpu(), inputs.cpu()).item()
                return loss_val

            except Exception:
                return -1e5
