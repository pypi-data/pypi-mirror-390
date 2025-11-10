__all__ = [
    "OptimizerWrapper",
    "get_adamw_optimizer",
    "get_trainable_modules",
    "grad_clip",
]
import torch
import numpy as np
from pathlib import Path
from warnings import warn
from lt_utils.common import *
from lt_tensor.common import *
import torch.nn.functional as F
from torch.optim import Optimizer
from lt_tensor.model_base import Model
from torch.amp.grad_scaler import GradScaler
from lt_utils.file_ops import is_pathlike, find_files
from lt_utils.misc_utils import log_traceback, filter_kwargs


class OptimizerWrapper:
    def __init__(
        self,
        optimizers: Dict[str, Optimizer] = {},
        schedulers: Dict[str, optim.lr_scheduler.LRScheduler] = {},
    ):
        self.optimizers = optimizers
        self.schedulers = schedulers
        self.steps = 0
        self._warned_once = {"accumulation_zero_grad": False}

        self.keys = list(optimizers.keys())

    def state_dict(self):
        std = {
            "optimizers": [],
            "schedulers": [],
            "steps": self.steps,
        }
        for k, v in self.optimizers.items():
            try:
                std["optimizers"].append({k: v.state_dict()})
            except Exception as e:
                log_traceback(e, title=f"Optimizer loading key {k}")
        for k, v in self.schedulers.items():
            try:
                std["schedulers"].append({k: v.state_dict()})
            except Exception as e:
                log_traceback(e, title=f"Scheduler loading key {k}")
        return std.copy()

    def load_state(
        self,
        path: Union[str, Path],
        not_exist_ok: bool = False,
        *,
        map_location: Optional[Any] = None,
        weights_only: bool = False,
    ):
        is_pathlike(path, validate=True)
        path = Path(path)
        exists = path.exists()
        if not exists:
            assert not_exist_ok, f"The provided path '{path}' does not exist!"
            return
        if path.is_file():
            data = torch.load(
                str(path), weights_only=weights_only, map_location=map_location
            )
        else:
            file = find_files(path, ["optimizers.pt"], maximum=1)
            if not file:
                assert (
                    not_exist_ok
                ), f"Unable to find an 'optimizers.pt' or 'optim.pt' ath the path '{str(path)}'"
                return None
            data = torch.load(
                file[0], weights_only=weights_only, map_location=map_location
            )
        self.load_state_dict(data)

    def step(
        self,
        keys: Optional[Union[str, List[str]]] = None,
        scaler: Optional[GradScaler] = None,
        perform_scheduler_step: bool = False,
        *args,
        **kwargs,
    ):
        if not keys:
            keys = self.keys
        else:
            if isinstance(keys, str):
                keys = [keys]
            elif isinstance(keys, (list, tuple)):
                keys = [x for x in keys if isinstance(x, str) and x in self.keys]
            else:
                raise ValueError(f"Invalid type for keys: {keys}")

        if keys:
            self.steps += 1

            for k in keys:
                if scaler is not None:
                    scaler.step(self.optimizers[k])
                    scaler.update()
                else:
                    self.optimizers[k].step()
            if perform_scheduler_step:
                self.scheduler(keys, *args)

    def zero_grad(
        self,
        keys: Optional[Union[str, List[str]]] = None,
        set_to_none: bool = False,
        *args,
        **kwargs,
    ):
        if keys:
            if isinstance(keys, str):
                self.optimizers[keys].zero_grad(set_to_none)
            else:
                for key in keys:
                    self.optimizers[key].zero_grad(set_to_none)
        else:
            for v in self.optimizers.values():
                v.zero_grad()

    def scheduler(
        self, key: Optional[Union[str, List[str]]] = None, *args, ret_lrs: bool = False
    ):
        if self.schedulers:
            if key is not None:
                if isinstance(key, str):
                    self.schedulers[key].step(*args)
                elif isinstance(key, (list, tuple)):
                    for k in key:
                        if k in self.schedulers:
                            self.schedulers[k].step(*args)
            else:
                for k, v in self.schedulers.items():
                    v.step(*args)

        if ret_lrs:
            return self.get_lr(key)

    def load_state_dict(self, state_dict: Dict[str, List[Dict[str, Any]]]):
        optimizers = state_dict["optimizers"]
        schedulers = state_dict["schedulers"]
        self.steps = state_dict.get("steps", 0)
        for otm in optimizers:
            for k, v in otm.items():
                try:
                    if k in self.optimizers:
                        self.optimizers[k].load_state_dict(v)
                    else:
                        print(f"Key '{k}' does not exist within optimizers. Skipped")
                except Exception as e:
                    log_traceback(e, title=f"load_state_dict -> Optimizer key: {k}")
        for scheduler in schedulers:
            for k, v in scheduler.items():
                try:
                    if k in self.schedulers:
                        self.schedulers[k].load_state_dict(v)
                    else:
                        print(
                            f"Key '{k}' does not exist within the schedulers. Skipped"
                        )
                except Exception as e:
                    log_traceback(e, title=f"load_state_dict -> Scheduler key: {k}")

    def save_state(self, path: Union[str, Path]):
        is_pathlike(path, validate=True)
        path = Path(path)
        if path.name.endswith((".pt", ".pth", ".ckpt", ".state")):
            name = path.name
            path = path.parent
        else:
            name = "optimizers.pt"
        path.mkdir(exist_ok=True, parents=True)
        path = Path(path, name)
        torch.save(self.state_dict(), str(path))

    def setup_scheduler(
        self,
        optim_key: str,
        scheduler_fn: Callable[[Optimizer, Any], optim.lr_scheduler.LRScheduler],
        **scheduler_kwargs,
    ):
        assert optim_key in self.optimizers
        self.schedulers[optim_key] = scheduler_fn(
            self.optimizers[optim_key],
            **filter_kwargs(scheduler_fn, False, **scheduler_kwargs),
        )

    def get_lr(
        self, keys: Optional[Union[str, List[str]]] = None
    ) -> Union[List[Dict[str, float]], float]:
        if not self.keys:
            return 0.0
        lrs = []
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                if keys in self.optimizers:
                    lrs = [x["lr"] for x in self.optimizers[keys].param_groups]
            else:
                for k in keys:
                    lrs.append(
                        {
                            k: [
                                x["lr"]
                                for x in self.optimizers[k].param_groups
                                if k in self.optimizers
                            ]
                        }
                    )
        else:
            for k, v in self.optimizers.items():
                lrs.append({k: x["lr"] for x in v.param_groups})
        if not lrs:
            return 0.0
        return np.mean(lrs)

    def _set_lr(self, new_lr: float, opt: str):
        for p in self.optimizers[opt].param_groups:
            if isinstance(p["lr"], Tensor):
                p["lr"].fill_(new_lr)
            else:
                p["lr"] = new_lr

    def set_lr(
        self,
        new_lr: float = 1e-4,
        keys: Optional[Union[str, List[str]]] = None,
    ) -> Union[List[Dict[str, float]], Dict[str, float]]:
        if keys and isinstance(keys, (str, list, tuple)):
            if isinstance(keys, str):
                self._set_lr(new_lr, keys)
            else:
                for key in keys:
                    self._set_lr(new_lr, key)
        else:
            for key in self.keys:
                self._set_lr(new_lr, key)


class ContentData(OrderedDict):
    model: Optional[Union[nn.Module, Model]] = None
    optimizer: Optional[Union[nn.Module, Model]] = None
    scheduler: Optional[optim.lr_scheduler.LRScheduler] = None
    gradient_clip: Optional[float] = None
    steps: int = 0

    def __init__(
        self,
        model: Union[nn.Module, Model],
        optimizer: Optimizer,
        scheduler: Optional[optim.lr_scheduler.LRScheduler] = None,
        gradient_clip: Optional[float] = None,
        steps: int = 0,
    ):
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.gradient_clip = gradient_clip
        self.steps = steps


def grad_clip(model: Union[Model, nn.Module], clip_value: float = 1.0):
    if clip_value > 0:
        return nn.utils.clip_grad_norm_(model.parameters(), max_norm=clip_value)
    return nn.utils.clip_grad_norm_(model.parameters(), max_norm=1e4)


def get_trainable_modules(
    *models: nn.Module,
    weight_decay_1: float = 0.01,
    weight_decay_2: float = 0.01,
    **kwargs,
) -> Tuple[List[nn.Parameter], List[nn.Parameter]]:
    group_sz_sm = []
    group_sz_lg = []
    for model in models:
        for param in model.parameters():
            if not param.requires_grad:
                continue
            if param.ndim < 2:
                group_sz_sm.append(param)
            else:
                group_sz_lg.append(param)

    return [
        {"params": group_sz_lg, "weight_decay": weight_decay_1},
        {"params": group_sz_sm, "weight_decay": weight_decay_2},
    ]


def get_grad_only(
    *models: Model,
    weight_decay: float = 0.1,
):
    parameters = []
    for model in models:
        for param in model.parameters():
            if param.requires_grad:
                parameters.append(param)
    return [
        {
            "params": parameters,
            "weight_decay": weight_decay,
        }
    ]


def get_adamw_optimizer(
    *models: Union[nn.Module, Model],
    lr: float = 1e-3,
    betas: Tuple = (0.9, 0.999),
    eps: float = 1e-8,
    use_fused_if_available: bool = False,
    module_processor: Optional[
        Callable[[Tuple[nn.Module, ...]], List[Dict[str, Union[Tensor, Any]]]]
    ] = None,
    **kwargs,
) -> optim.AdamW:
    from lt_tensor.misc_utils import is_fused_available

    if module_processor is None:
        optim_groups = get_trainable_modules(
            *models, **filter_kwargs(get_trainable_modules, False, [], **kwargs)
        )
    else:
        optim_groups = module_processor(
            *optim_groups, **filter_kwargs(module_processor, False, [], **kwargs)
        )
    use_fused = (
        use_fused_if_available and is_fused_available() and torch.cuda.is_available()
    ) or None

    return optim.AdamW(
        optim_groups,
        lr=lr,
        betas=betas,
        eps=eps,
        fused=use_fused,
        **filter_kwargs(optim.AdamW, False, ["params", "fused"], **kwargs),
    )


def get_optimizer(
    *models: Union[nn.Module, Model],
    optimizer: Type[optim.Optimizer] = optim.Adam,
    lr: float = 1e-3,
    module_processor: Optional[
        Callable[[Tuple[nn.Module, ...]], List[Dict[str, Union[Tensor, Any]]]]
    ] = None,
    **kwargs,
) -> Union[Optimizer, optim.Adam, optim.SGD]:

    if module_processor is None:
        group_decay_sm, group_decay_lg = get_trainable_modules(*models, **kwargs)

        optim_groups = get_grad_only(
            *models, **filter_kwargs(get_trainable_modules, False, [], **kwargs)
        )
    else:

        optim_groups = module_processor(
            *models, **filter_kwargs(module_processor, False, [], **kwargs)
        )
    return optimizer(
        params=optim_groups,
        lr=lr,
        **filter_kwargs(optimizer, False, ["params"], **kwargs),
    )
