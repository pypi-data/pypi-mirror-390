__all__ = ["GatedResidualBlock"]
import torch
from torch import Tensor

from lt_utils.common import *
from .base import _GatedResblockBase


class GatedResidualBlock(_GatedResblockBase):
    def forward(self, x: Tensor, cond: Optional[Tensor] = None):
        res_base = x
        x = self._apply_cond(x, cond=cond)
        residual = torch.zeros_like(x)
        for i, b in enumerate(self.dilation_blocks):
            y_fwd, y_bwd = b["conv"](b["activ_1"](res_base))
            skip = self._get_gated(y_fwd, y_bwd)
            res_base = b["proj"](b["activ_2"]((skip)))
            residual = (res_base * self.skip_sz) + residual
        return x + residual
