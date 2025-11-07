from __future__ import annotations

__all__ = [
    "RotaryPositionalEncoding",
    "SinusoidalPositionalEncoding",
]

import math
from lt_utils.common import *
from lt_tensor.common import *


class SinusoidalPositionalEncoding(nn.Module):
    def __init__(self, d_model: int, base: float = 10000.0):
        super().__init__()
        self.d_model = d_model
        self.base = base

        inv_freq = 1.0 / (base ** (torch.arange(0, d_model, 2).float() / d_model))
        self.register_buffer("inv_freq", inv_freq)

        self.register_buffer("phase", torch.zeros(1, d_model))

    @torch.no_grad()
    def _get_positions(
        self,
        sz: int,
        device: torch.device,
        dtype: torch.dtype,
        positions: Optional[Tensor] = None,
    ):
        if positions is None:
            positions = torch.arange(sz, device=device, dtype=dtype).unsqueeze(1)
        sinusoid_inp = positions * self.inv_freq.unsqueeze(0)
        pe = torch.cat([torch.sin(sinusoid_inp), torch.cos(sinusoid_inp)], dim=1)
        pe = pe[:, : self.d_model] + self.phase

        pe = pe.unsqueeze(0)
        return pe

    def forward(self, x: Tensor, positions: Optional[Tensor] = None):
        pe = self._get_positions(x.size(1), x.device, x.dtype, positions=positions)
        enc = x + pe
        return enc


class RotaryPositionalEncoding(nn.Module):
    def __init__(
        self,
        d_model: int,
        rotary_dim: Optional[int] = None,
        reshape_output: bool = False,
        base: float = 10000.0,
    ):
        """
        Learnable Rotary Positional Encoding (RoPE+)

        Args:
            d_model: hidden dimension
            rotary_dim: number of dims to apply rotation on (default = all)
            base: base frequency scale for sinusoidal frequencies
        """
        super().__init__()
        self.d_model = d_model
        self.rotary_dim = rotary_dim or d_model
        self.reshape_output = reshape_output
        assert self.rotary_dim % 2 == 0, "rotary_dim must be even"

        inv_freq = 1.0 / (
            base ** (torch.arange(0, self.rotary_dim, 2).float() / self.rotary_dim)
        )
        self.register_buffer("inv_freq", inv_freq)

        # Learnable components
        self.register_buffer("freq_scale", torch.ones_like(inv_freq))

        self.register_buffer("phase", torch.zeros(1, 1, self.rotary_dim))

    def forward(self, x: Tensor):
        """
        Applies learnable rotary positional encoding.

        Args:
            x: Tensor [B, seq_len, d_model]
            mask: Optional mask [B, seq_len], True for valid positions.
        Returns:
            Tensor [B, seq_len, d_model]
        """
        B, T = x.shape[:2]
        t = torch.arange(T, device=x.device, dtype=x.dtype)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq * self.freq_scale)
        emb = torch.cat([freqs, freqs], dim=-1) + self.phase

        cos = emb.cos()[None, :, :]
        sin = emb.sin()[None, :, :]

        x_rot = self._apply_rotary(x, cos, sin)
        if self.reshape_output:
            x_rot = x_rot.view(B, T, -1)
        return x_rot

    def _apply_rotary(self, x: Tensor, cos: Tensor, sin: Tensor):
        x_rot = x[..., : self.rotary_dim]
        x_pass = x[..., self.rotary_dim :] if self.rotary_dim < self.d_model else None

        x1, x2 = x_rot[..., ::2], x_rot[..., 1::2]
        x_rotated = torch.stack((-x2, x1), dim=-1).reshape_as(x_rot)

        x_rot = (x_rot * cos) + (x_rotated * sin)

        if x_pass is not None:
            x_rot = torch.cat([x_rot, x_pass], dim=-1)

        return x_rot
