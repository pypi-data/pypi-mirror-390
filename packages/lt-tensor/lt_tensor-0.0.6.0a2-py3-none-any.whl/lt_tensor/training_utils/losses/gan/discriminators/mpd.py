__all__ = ["MultiPeriodDiscriminator", "MPDConfig"]
from lt_utils.common import *


from lt_tensor.common import F, torch, Tensor, nn, Model, ModelConfig
from lt_tensor.model_zoo.convs import ConvBase

# Typing helpers
TP_C1_O1: TypeAlias = Callable[[Tensor], Tensor]  #  modules related
TP_C2_O1: TypeAlias = Callable[[Tensor, Tensor], Tensor]  # loss related


def ch_size_lambda(multiplier: float):
    """Helps to resize channels in a fast manner."""
    return lambda x: max(int(x * multiplier), 1)


class MPDConfig(ModelConfig):
    def __init__(
        self,
        mpd_reshapes: list[int] = [2, 3, 5, 7, 11],
        kernels: list[int] = [1, 3, 5, 7, 9],
        strides: list[int] = [1, 2, 4, 8, 8],
        dilations: list[int] = [1, 1, 2, 4, 4],
        post_dilations: list[int] = [1, 1, 1, 2, 2],
        groups: list[int] = [1, 1, 1, 1, 1],
        scales: list[int] = [1.0, 1.0, 1.0, 1.0, 1.0],
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = "weight_norm",
        *args,
        **kwargs
    ):
        super().__init__(
            mpd_reshapes=mpd_reshapes,
            kernels=kernels,
            strides=strides,
            groups=groups,
            scales=scales,
            norm=norm,
            dilations=dilations,
            post_dilations=post_dilations,
        )


class PeriodDiscriminator(ConvBase):
    def __init__(
        self,
        period: int,
        discriminator_channel_multi: Number = 1,
        kernel_size: int = 5,
        stride: int = 3,
        dilation: int = 1,
        post_dilation: int = 1,
        groups: int = 1,
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = "weight_norm",
        loss_fn: TP_C2_O1 = nn.L1Loss(),
    ):
        super().__init__()
        self.period = period
        ch_m = ch_size_lambda(discriminator_channel_multi)
        _sec_dil = dilation // 2 + 1
        kwargs_cnns = dict(
            kernel_size=(kernel_size, 1),
            stride=(stride, 1),
            dilation=(dilation, _sec_dil),
            padding=(
                self.get_padding(kernel_size, dilation),
                self.get_padding(1, _sec_dil),
            ),
            norm=norm,
        )
        self.loss_fn = loss_fn
        self.activation = nn.LeakyReLU(0.1)
        self.convs = nn.ModuleList(
            [
                nn.Sequential(
                    self.get_2d_conv(1, ch_m(32), **kwargs_cnns),
                    self.activation,
                ),
                nn.Sequential(
                    self.get_2d_conv(ch_m(32), ch_m(128), **kwargs_cnns, groups=groups),
                    self.activation,
                ),
                nn.Sequential(
                    self.get_2d_conv(
                        ch_m(128), ch_m(512), **kwargs_cnns, groups=groups
                    ),
                    self.activation,
                ),
                nn.Sequential(
                    self.get_2d_conv(
                        ch_m(512), ch_m(1024), **kwargs_cnns, groups=groups
                    ),
                    self.activation,
                ),
                nn.Sequential(
                    self.get_2d_conv(
                        ch_m(1024),
                        ch_m(1024),
                        kernel_size=(kernel_size, 1),
                        dilation=_sec_dil,
                        padding=(
                            self.get_padding(kernel_size, _sec_dil),
                            self.get_padding(1, _sec_dil),
                        ),
                    ),
                    self.activation,
                ),
            ]
        )

        self.conv_post: TP_C1_O1 = self.get_2d_conv(
            ch_m(1024),
            1,
            (3, 1),
            dilation=post_dilation,
            padding=(
                self.get_padding(3, post_dilation),
                self.get_padding(1, post_dilation),
            ),
            norm=norm,
        )

    def generator_loss(self, fake_wave: Tensor) -> Tensor:
        res = self(fake_wave)
        return torch.mean((res - 1.0) ** 2)

    def discriminator_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        fake = self.train_step(fake_wave.clone().detach())
        real = self.train_step(real_wave)
        loss_real = torch.mean((real - 1.0) ** 2)
        loss_fake = torch.mean(fake**2)
        return loss_real, loss_fake

    def feature_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
        lambda_loss: float = 1.0,
    ) -> Tensor:
        with torch.no_grad():
            feats_real = self(real_wave, feat_collection=True)
        feats_fake = self(fake_wave, feat_collection=True)

        loss = 0
        for rf, ff in zip(feats_real, feats_fake):
            loss += torch.mean(torch.abs(rf - ff)) * lambda_loss
        return loss

    def forward(
        self,
        x: Tensor,
        feat_collection: bool = False,
    ) -> Union[Tensor, List[Tensor]]:
        if feat_collection:
            feat_map = []

        # 1d to 2d [unchanged from original]
        b, c, t = x.shape
        if t % self.period != 0:  # pad first
            n_pad = self.period - (t % self.period)
            x = F.pad(x, (0, n_pad), "reflect")
            t = t + n_pad
        x = x.view(b, c, t // self.period, self.period)

        for l in self.convs:
            x = l(x)
            if feat_collection:
                feat_map.append(x)

        if feat_collection:
            return feat_map

        x = self.conv_post(x).flatten(1, -1)

        return x


class MultiPeriodDiscriminator(Model):
    def __init__(self, cfg: MPDConfig = MPDConfig()):
        super().__init__()
        self.cfg = cfg if isinstance(cfg, MPDConfig) else MPDConfig(**cfg)
        self.discriminators: List[PeriodDiscriminator] = nn.ModuleList(
            [
                PeriodDiscriminator(
                    mp,
                    kernel_size=ks,
                    stride=st,
                    dilation=dl,
                    norm=self.cfg.norm,
                    discriminator_channel_multi=sc,
                    groups=gp,
                    post_dilation=pdl,
                )
                for (mp, ks, st, gp, sc, dl, pdl) in (
                    zip(
                        self.cfg.mpd_reshapes,
                        self.cfg.kernels,
                        self.cfg.strides,
                        self.cfg.groups,
                        self.cfg.scales,
                        self.cfg.dilations,
                        self.cfg.post_dilations,
                    )
                )
            ]
        )
        self.init_weights(
            base_norm_type="normal",
            small_norm_type="zeros",
            base_norm_kwargs={"mean": 0.0, "std": 0.03},
        )

    def generator_loss(self, fake_wave: Tensor) -> Tensor:
        res = self(fake_wave)
        return torch.mean((res - 1.0) ** 2)

    def discriminator_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        fake = self.train_step(fake_wave.clone().detach())
        real = self.train_step(real_wave)
        loss_real = torch.mean((real - 1.0) ** 2)
        loss_fake = torch.mean(fake**2)
        return loss_real, loss_fake

    def feature_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
    ) -> Tensor:
        feature_loss = 0.0
        for D in self.discriminators:
            feature_loss += D.feature_loss(fake_wave, real_wave)
        return feature_loss

    def forward(self, x: Tensor) -> Union[Tensor, List[Tensor]]:
        results = []
        B = x.shape[0]
        for D in self.discriminators:
            outputs = D(x=x, feat_collection=False)
            results.append(outputs)
        output = torch.concat(results, dim=1)
        return output.flatten(1, -1)
