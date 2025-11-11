__all__ = ["SineGen"]

from lt_utils.common import *
from lt_tensor.common import *
import torch.nn.functional as F
from lt_tensor.model_zoo.convs import ConvBase, is_conv
from lt_tensor.model_zoo.residual import PoolResBlock2D

class SineGen(Model):

    def __init__(
        self,
        sample_rate: int = 24000,
        upscale_rate: int = 9,
        harmonic_num: int = 8,
        sine_amp: float = 0.1,
        noise_std: float = 0.003,
        voiced_threshold: float = 10,
    ):
        super().__init__()
        self.sine_amp = sine_amp
        self.noise_std = noise_std
        self.harmonic_num = harmonic_num
        self.sample_rate = sample_rate
        self.upscale_rate = upscale_rate
        self.voiced_threshold = voiced_threshold
        self.register_buffer(
            "hum", torch.arange(1, self.harmonic_num + 1, dtype=torch.float32)
        )

    def __call__(self, *args, **kwds) -> Tensor:
        return super().__call__(*args, **kwds)

    def forward(self, f0: Tensor):
        f0 = f0 * self.hum

        rad_values = (f0 / self.sample_rate) % 1

        rand_ini = torch.randn(f0.size(0), f0.size(-1), device=f0.device)
        rand_ini[:, 0] = 0
        rad_values[:, 0, :] = rad_values[:, 0, :] + rand_ini
        sine_waves = (
            F.interpolate(
                rad_values.transpose(1, 2),
                scale_factor=1 / self.upscale_rate,
                mode="linear",
            )
            .transpose(1, 2)
            .sin()
        )
        uv = (f0 > self.voiced_threshold).to(dtype=torch.float32)
        noise_amp = uv * self.noise_std + (1 - uv) * self.sine_amp / 3
        noise = torch.randn_like(sine_waves)
        proj = sine_waves * uv + (noise * noise_amp)
        return dict(
            sine=proj,
            noise=noise,
            uv=uv,
            noise_amp=noise_amp,
        )
