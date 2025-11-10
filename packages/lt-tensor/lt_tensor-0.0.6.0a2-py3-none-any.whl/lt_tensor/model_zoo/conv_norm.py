__all__ = ["Conv1dNorm", "ConvNormConfig"]
import math
from lt_utils.common import *
from lt_tensor.common import *
from lt_tensor.activations_utils import get_activation, ACTIV_NAMES_TP
from lt_tensor.model_zoo.convs import ConvBase


class ConvNormConfig(ModelConfig):
    param_norm: Optional[Literal["param_norm", "spectral_norm"]] = None
    channels: List[int] = [128, 128]
    kernel_size: List[int] = [1, 1]
    dilation: List[int] = [1, 1]
    stride: List[int] = [1, 1]
    groups: List[int] = [1, 1]
    padding: List[int] = [0, 0]
    activation_kwargs: Dict[str, Any] = dict()
    activation: ACTIV_NAMES_TP = "gelu"
    norm_type: Optional[Literal["layer", "group"]] = "group"
    mask_value: float = 0.0
    dropout: float = 0.02
    bias: bool = True
    eps: float = 1e-5
    norm_bias: bool = True
    affine = True

    def __init__(
        self,
        channels: List[int] = [128, 128],
        kernel_size: List[int] = [1, 1],
        dilation: List[int] = [1, 1],
        stride: List[int] = [1, 1],
        groups: List[int] = [1, 1],
        padding: List[int] = [0, 0],
        activation: ACTIV_NAMES_TP = "gelu",
        activation_kwargs: Dict[str, Any] = dict(),
        mask_value: float = 0.0,
        bias: bool = True,
        eps: float = 1e-5,
        dropout: float = 0.2,
        param_norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
        affine=True,
        norm_bias: bool = True,
        *args,
        **kwargs,
    ):
        super().__init__(
            **dict(
                param_norm=param_norm,
                eps=eps,
                bias=bias,
                stride=stride,
                groups=groups,
                dropout=dropout,
                channels=channels,
                dilation=dilation,
                activation=activation,
                mask_value=mask_value,
                kernel_size=kernel_size,
                activation_kwargs=activation_kwargs,
                padding=padding,
                norm_bias=norm_bias,
                affine=affine,
            )
        )

    def __len__(self):
        return min(
            [
                len(x)
                for x in [
                    self.channels,
                    self.kernel_size,
                    self.stride,
                    self.dilation,
                    self.groups,
                    self.padding,
                ]
            ]
        )

    def fix_lists(self, mode: Literal["crop_larger", "pad_smaller"] = "pad_smaller"):
        all_lists = [
            self.channels,
            self.kernel_size,
            self.stride,
            self.dilation,
            self.groups,
            self.padding,
        ]
        if mode == "crop_larger":
            min_len = min([len(x) for x in all_lists])
            if not min_len:  # 0
                raise ValueError("Empty list found, cannot crop.")
            (
                self.channels,
                self.kernel_size,
                self.stride,
                self.dilation,
                self.groups,
                self.padding,
            ) = [list(lst)[:min_len] for lst in all_lists]
        else:
            max_len = max(len(lst) for lst in all_lists)

            def pad(lst):
                if not lst:
                    raise ValueError("Empty list found, cannot pad.")
                if len(lst) < max_len:
                    lst.extend([lst[-1]] * (max_len - len(lst)))
                return lst

            (
                self.channels,
                self.kernel_size,
                self.stride,
                self.dilation,
                self.groups,
                self.padding,
            ) = [pad(lst) for lst in all_lists]


class Conv1dNorm(ConvBase):
    def __init__(
        self,
        config: ConvNormConfig,
        initial_channel_size: int = 1,
        layer_id: int = 0,
    ):
        super().__init__()
        if not isinstance(config, (ConvNormConfig, ModelConfig)):
            assert isinstance(config, dict), f"Invalid config: {config}"
            config = ConvNormConfig(**config)
        self.config = config

        self.in_conv_dim = (
            config.channels[layer_id - 1] if layer_id > 0 else initial_channel_size
        )
        self.out_conv_dim = config.channels[layer_id]

        self.mask_value = self.config.mask_value
        self.activation = get_activation(
            self.config.activation, **self.config.activation_kwargs
        )

        self.cnn = self.get_1d_conv(
            self.in_conv_dim,
            self.out_conv_dim,
            kernel_size=config.kernel_size[layer_id],
            dilation=config.dilation[layer_id],
            groups=config.groups[layer_id],
            stride=config.stride[layer_id],
            padding=config.padding[layer_id],
            bias=config.bias,
            norm=config.param_norm,
        )
        self.dropout = (
            nn.Identity()
            if self.config.dropout <= 0
            else nn.Dropout(self.config.dropout)
        )

        self.norm_type: Optional[Literal["layer", "group"]] = self.config.norm_type
        if self.norm_type == "layer":
            self.layer_norm = nn.LayerNorm(
                self.out_conv_dim,
                self.config.eps,
                elementwise_affine=self.config.affine,
                bias=self.config.norm_bias,
            )
        elif self.norm_type == "group":
            self.layer_norm = nn.GroupNorm(
                num_groups=self.out_conv_dim,
                num_channels=self.out_conv_dim,
                affine=self.config.affine,
            )
        else:
            self.layer_norm = nn.Identity()

    def forward(self, x: Tensor, mask: Optional[Tensor] = None):
        if mask is not None:
            x.masked_fill_(mask, self.mask_value)
        x = self.cnn(x)
        if self.norm_type == "layer":
            x = x.transpose(-2, -1)
            x = self.layer_norm(x)
            x = x.transpose(-1, -2)
        else:
            x = self.layer_norm(x)
        x = self.activation(x)
        x = self.dropout(x)
        return x
