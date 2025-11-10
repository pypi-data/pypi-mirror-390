__all__ = ["DiffusionTimeEmbedding"]
import math
from lt_utils.common import *
from lt_tensor.common import *
import torch.nn.functional as F
from lt_tensor.model_zoo.convs import ConvBase, is_conv
from lt_tensor.activations_utils import get_activation, ACTIV_NAMES_TP


class DiffusionTimeEmbedding(Model):
    def __init__(
        self,
        max_steps: int = 1000,
        emb_dim: int = 256,
        hidden_dim: int = 768,
        freq_scale: float = 10.0,
        activation: ACTIV_NAMES_TP = "silu",
        activation_kwargs: Dict[str, Any] = {},
    ):
        super().__init__()
        assert emb_dim % 2 == 0, "emb_dim must be divisible by 2"
        self.max_steps = max_steps
        self.sin_cos_dim = emb_dim // 2
        self.freq_scale = freq_scale

        # Precompute embedding table (acts as a lookup)
        self.register_buffer(
            "embedding", self._build_embedding(max_steps), persistent=False
        )

        # Flexible projection network
        self.net = nn.Sequential(
            nn.Linear(emb_dim, hidden_dim),
            get_activation(activation, **activation_kwargs),
            nn.Linear(hidden_dim, emb_dim),
            get_activation(activation, **activation_kwargs),
        )

    def forward(self, diffusion_step: Tensor):
        """
        diffusion_step: [B] integer timesteps (0..max_steps-1)
        returns: [B, output_dim]
        """
        # ensure indexing tensor
        diffusion_step = torch.as_tensor(diffusion_step, dtype=torch.long)
        step_emb = self.embedding[diffusion_step]  # [B, input_dim * 2]
        return self.net(step_emb)

    def _build_embedding(self, max_steps: int) -> torch.Tensor:
        """
        Create Fourier features across timesteps.
        The scaling function is fully open: f(d, i) = step * scale^(i / (input_dim-1))
        """
        steps = torch.arange(max_steps).unsqueeze(1)  # [T, 1]
        dims = torch.arange(self.sin_cos_dim).unsqueeze(0)  # [1, D]

        # Exponential frequency scaling
        freq = self.freq_scale ** (dims / (self.sin_cos_dim - 1))
        table = steps * freq  # [T, D]
        table = torch.cat([torch.sin(table), torch.cos(table)], dim=1)  # [T, 2D]
        return table
