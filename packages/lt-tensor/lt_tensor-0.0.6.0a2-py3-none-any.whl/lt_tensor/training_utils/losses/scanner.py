__all__ = ["LossScanner"]

import optuna
from lt_utils.common import *
from lt_tensor.common import *
from abc import ABC, abstractmethod


class LossScanner(ABC):
    def __init__(
        self,
        trials: int = 512,
        show_progress_bar: bool = True,
        study_direction: Literal["maximize", "minimize"] = "maximize",
        *args,
        **kwargs
    ):
        self.study_direction = study_direction
        self.show_progress_bar = show_progress_bar
        self.trials = trials
        self.restart_study()

    @abstractmethod
    def objective(
        self,
        trial: optuna.trial.Trial,
        inputs: Tensor,
        labels: Tensor,
    ):
        raise NotImplementedError()

    def restart_study(self):
        optuna.logging.disable_default_handler()
        optuna.logging.set_verbosity(optuna.logging.ERROR)
        self.study = optuna.create_study(direction=self.study_direction)

    def run_search(
        self,
        fake_audio: Tensor,
        real_audio: Tensor,
    ):
        """Runs Optuna to find configurations exposing model weaknesses."""
        self.study.optimize(
            lambda trial: self.objective(trial, real_audio, fake_audio),
            n_trials=self.trials,
            show_progress_bar=self.show_progress_bar,
        )
        return self.study.best_params, self.study.best_value

    def __call__(
        self,
        inputs: Tensor,
        labels: Tensor,
        top_k: int = 32,
    ):
        """Returns top-k configurations to add to the training ensemble."""

        best_param, best_value = self.run_search(labels, inputs)
        trials = sorted(self.study.trials, key=lambda t: t.value, reverse=True)
        return dict(
            best_param=best_param,
            best_value=best_value,
            top_k=[t.params for t in trials[:top_k]],
        )
