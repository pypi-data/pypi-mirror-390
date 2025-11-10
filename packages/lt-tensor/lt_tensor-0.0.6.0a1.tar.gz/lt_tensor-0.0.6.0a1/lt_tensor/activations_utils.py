__all__ = ["get_activation", "ACTIVATIONS_MAP", "get_callable_activation"]
from torch import nn, Tensor
from lt_utils.common import *
from lt_utils.misc_utils import log_traceback, filter_kwargs
from lt_tensor.model_zoo.activations.alias_free import (
    Activation1d as Alias1D,
    Activation2d as Alias2D,
)
from lt_tensor.model_zoo.activations.snake import Snake, SnakeBeta
import inspect
from lt_tensor._misc._type_hints import ACTIV_NAMES_TP

ACTIVATIONS_MAP = {
    "relu": nn.ReLU,
    "leaky_relu": nn.LeakyReLU,
    "leakyrelu": nn.LeakyReLU,
    "relu6": nn.ReLU6,
    "rrelu": nn.RReLU,
    "tanh": nn.Tanh,
    "hardtanh": nn.Hardtanh,
    "sigmoid": nn.Sigmoid,
    "logsigmoid": nn.LogSigmoid,
    "hardsigmoid": nn.Hardsigmoid,
    "softmin": nn.Softmin,
    "softmax": nn.Softmax,
    "logsoftmax": nn.LogSoftmax,
    "softmax2d": nn.Softmax2d,
    "multiheadattention": nn.MultiheadAttention,
    "mish": nn.Mish,
    "gelu": nn.GELU,
    "celu": nn.CELU,
    "elu": nn.ELU,
    "prelu": nn.PReLU,
    "silu": nn.SiLU,
    "selu": nn.SELU,
    "glu": nn.GLU,
    "hardswish": nn.Hardswish,
    "softplus": nn.Softplus,
    "hardshrink": nn.Hardshrink,
    "softshrink": nn.Softshrink,
    "tanhshrink": nn.Tanhshrink,
    "threshold": nn.Threshold,
    "aliasfree1d": Alias1D,
    "aliasfree2d": Alias2D,
    "snake": Snake,
    "snakebeta": SnakeBeta,
}

_ACTIVATION_LIKE_TP: TypeAlias = Union[nn.Module, Callable[[Tensor], Tensor]]


def get_callable_activation(
    activation: ACTIV_NAMES_TP, *args, **kwargs
) -> Type[_ACTIVATION_LIKE_TP]:
    activation = activation.lower().strip()
    if activation == 'leakyrelu':
        activation == 'leaky_relu'
    assert activation in ACTIVATIONS_MAP, f"Invalid activation {activation}"
    current_activation = ACTIVATIONS_MAP[activation]
    clear_kwargs = {}
    has_args = list(inspect.signature(current_activation).parameters.keys())
    if not has_args:
        return lambda: current_activation()
    if kwargs:
        clear_kwargs = filter_kwargs(current_activation, False, [], **kwargs)
    return lambda: current_activation(*args, **clear_kwargs)


def get_activation(activation: ACTIV_NAMES_TP, *args, **kwargs) -> _ACTIVATION_LIKE_TP:
    activation = activation.lower().strip()
    if activation == 'leakyrelu':
        activation == 'leaky_relu'
    assert activation in ACTIVATIONS_MAP, f"Invalid activation {activation}"
    current_activation = ACTIVATIONS_MAP[activation]
    clear_kwargs = {}
    has_args = list(inspect.signature(current_activation).parameters.keys())
    if not has_args:
        return current_activation()
    if kwargs:
        clear_kwargs = filter_kwargs(current_activation, False, [], **kwargs)
    return current_activation(*args, **clear_kwargs)
