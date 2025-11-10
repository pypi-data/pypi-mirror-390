__all__ = ["FilterDiscriminator", "MultiFilterDiscriminator"]
from lt_utils.common import *
from lt_tensor.common import *

from lt_tensor.model_zoo.convs import ConvBase
from lt_tensor.model_zoo import BidirectionalConv
from lt_tensor.processors.audio.misc import BandFilter
from lt_tensor.misc_utils import log_tensor


class FilterDiscriminator(ConvBase):
    def __init__(
        self,
        audio_channels_in: int = 1,
        initial_scale: int = 8,
        hidden_dim: int = 32,
        *,
        sr: Number = 24000,
        q_factor: float = 1.1539,
        central_freq: float = 32.0062,
        gain: float = 6.25,
        types_fn: List[
            Literal[
                "band",
                "lowpass",
                "highpass",
                "allpass",
                "bandpass",
                "bandreject",
                "bass",
                "treble",
                "equalizer",
            ]
        ] = "highpass",
        bi_cnn_kernel_size_fwd: int = 7,
        bi_cnn_kernel_size_bwd: int = 7,
        bi_cnn_dilation_fwd: int = 1,
        bi_cnn_dilation_bwd: int = 1,
        seed: Optional[int] = None,
        **kwargs
    ) -> None:
        super().__init__(seed=seed)
        self.activ = nn.LeakyReLU(0.1)
        self.filter = BandFilter(
            type_fn=types_fn,
            q_factor=q_factor,
            central_freq=central_freq,
            gain=gain,
            noise_csg=False,
            sr=sr,
            requires_grad=False,
            gain_requires_grad=False,
        )
        self.conv_in = nn.Conv1d(
            audio_channels_in,
            initial_scale,
            kernel_size=3,
            padding=1,
            bias=True,
        )

        p = lambda k, d: (k - 1) * d // 2
        initial_stride = initial_scale // 4 + 1
        self.bi_conv2d = BidirectionalConv(
            in_channels=1,
            out_channels=hidden_dim // 2,
            kernel_size=bi_cnn_kernel_size_fwd,
            stride=(initial_scale // 4 + 1, initial_scale // 4 + 1),
            kernel_size_bwd=bi_cnn_kernel_size_bwd,
            dilation=bi_cnn_dilation_fwd,
            dilation_bwd=bi_cnn_dilation_bwd,
            padding=p(bi_cnn_kernel_size_fwd, bi_cnn_dilation_fwd),
            padding_bwd=p(bi_cnn_kernel_size_bwd, bi_cnn_dilation_bwd),
            return_tuple=True,
            conv_dim="2d",
        )

        self.process = nn.ModuleList(
            [
                nn.Conv2d(
                    hidden_dim // 2,
                    hidden_dim,
                    kernel_size=(3, 3),
                    padding=(1, 1),
                ),
                nn.Conv2d(
                    hidden_dim,
                    hidden_dim,
                    kernel_size=(7, 7),
                    dilation=(2, 2),
                    padding=(p(7, 2), p(7, 2)),
                ),
                nn.Conv2d(
                    hidden_dim,
                    hidden_dim,
                    kernel_size=(3, 3),
                    stride=(2, 2),
                    padding=(1, 1),
                ),
                nn.Conv2d(
                    hidden_dim,
                    hidden_dim,
                    kernel_size=(7, 7),
                    dilation=(2, 2),
                    padding=(p(7, 2), p(7, 2)),
                ),
            ]
        )
        self.proj_out = nn.Conv2d(hidden_dim, 1, kernel_size=7, padding=3, bias=False)

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
        with torch.no_grad():
            feats_real = self(real_wave, feat_collection=True)
        feats_fake = self(fake_wave, feat_collection=True)

        loss = 0
        for rf, ff in zip(feats_real, feats_fake):
            loss += torch.mean(torch.abs(rf - ff))
        return loss

    def forward(self, x: Tensor, *, feat_collection: bool = False):
        features = []
        if x.ndim == 2:
            x = x.unsqueeze(0)
        filtered = self.filter(x)

        x = self.activ(self.conv_in(filtered))
        if feat_collection:
            features.append(x.flatten(1, -1))

        B, C, T = x.shape
        x = x.view(B, 1, C, T)
        gate_x, h_x = self.bi_conv2d(x)
        x = gate_x.sigmoid() * (1.0 + h_x.tanh())
        for L in self.process:
            x = self.activ(L(x))
            if feat_collection:
                features.append(x.flatten(1, -1))

        if feat_collection:
            return features

        x = self.proj_out(x)
        return x.view(B, 1, -1)


class MultiFilterDiscriminator(ConvBase):
    def __init__(
        self,
        audio_channels_in: int = 1,
        initial_scale: int = 8,
        hidden_dim: int = 32,
        *,
        sr: Number = 24000,
        q_factors: List[float] = [0.707, 1.1539, 3.6249],
        central_freq: List[float] = [4.1416, 32.0062, 1225.0787],
        gain: List[float] = [5.0, 5.0, 2.0],
        types_fn: List[
            Literal[
                "band",
                "lowpass",
                "highpass",
                "allpass",
                "bandpass",
                "bandreject",
                "bass",
                "treble",
                "equalizer",
            ]
        ] = ["highpass", "lowpass", "bass"],
        bi_cnn_kernel_size_fwd: List[int] = [7, 5, 3],
        bi_cnn_kernel_size_bwd: List[int] = [3, 5, 7],
        bi_cnn_dilation_fwd: List[int] = [1, 2, 4],
        bi_cnn_dilation_bwd: List[int] = [2, 4, 8],
        seed: Optional[int] = None,
        **kwargs
    ) -> None:
        super().__init__(seed=seed)
        TP: TypeAlias = Union[nn.ModuleList, List[FilterDiscriminator]]
        self.discriminators: TP = nn.ModuleList(
            [
                FilterDiscriminator(
                    audio_channels_in=audio_channels_in,
                    initial_scale=initial_scale,
                    hidden_dim=hidden_dim,
                    sr=sr,
                    q_factor=qf,
                    central_freq=cf,
                    gain=gn,
                    bi_cnn_kernel_size_fwd=k_fwd,
                    bi_cnn_kernel_size_bwd=k_bwd,
                    bi_cnn_dilation_fwd=d_fwd,
                    bi_cnn_dilation_dwd=d_bwd,
                    types_fn=tp,
                    seed=seed,
                )
                for qf, cf, gn, k_fwd, k_bwd, d_fwd, d_bwd, tp in zip(
                    q_factors,
                    central_freq,
                    gain,
                    bi_cnn_kernel_size_fwd,
                    bi_cnn_kernel_size_bwd,
                    bi_cnn_dilation_fwd,
                    bi_cnn_dilation_bwd,
                    types_fn,
                )
            ]
        )

    def feature_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
    ) -> Tensor:
        feature_loss = 0.0
        for D in self.discriminators:
            feature_loss += D.feature_loss(fake_wave, real_wave)
        return feature_loss

    def generator_loss(self, fake_wave: Tensor):
        res = self(fake_wave)
        return torch.mean((res - 1.0) ** 2)

    def discriminator_loss(
        self,
        fake_wave: Tensor,
        real_wave: Tensor,
    ):
        fake = self.train_step(fake_wave.clone().detach())
        real = self.train_step(real_wave)
        loss_real = torch.mean((real - 1.0) ** 2)
        loss_fake = torch.mean(fake**2)
        return loss_real, loss_fake

    def forward(self, x: Tensor):
        results = []
        B = x.shape[0]
        for D in self.discriminators:
            outputs = D(x=x, feat_collection=False)
            results.append(outputs)
        output = torch.concat(results, dim=1)
        return output.flatten(1, -1)
