__all__ = [
    "StyleEncoder",
    "AttentionPooling",
    "DurationPredictor",
    "DiffusionTimeEmbedding",
]

from lt_utils.common import *
from lt_tensor.common import *
import math
import torch.nn.functional as F
from lt_tensor.model_zoo.convs import ConvBase, is_conv
from lt_tensor.activations_utils import get_activation, ACTIV_NAMES_TP
from lt_tensor.model_zoo.diffusion import DiffusionTimeEmbedding


class DurationPredictor(ConvBase):
    def __init__(
        self,
        d_model: int = 128,
        exponential: bool = True,
        dilation: int = 1,
        n_layers: int = 2,
        dropout: float = 0.0,
        kernel_size: int = 3,
        mask_value: Number = 0.0,
        flatten_outputs: bool = True,
        bias_at_final_layer: bool = False,
        proj_activation: ACTIV_NAMES_TP = "silu",
        proj_activation_kwargs: Dict[str, Any] = dict(),
        layers_activations: ACTIV_NAMES_TP = "leakyrelu",
        layer_activations_kwargs: Dict[str, Any] = dict(),
        norm: Optional[Literal["weight_norm", "spectral_norm"]] = None,
    ):
        super().__init__()
        self.flatten_outputs = flatten_outputs
        pad = self.get_padding(kernel_size, dilation)
        n_layers = max(int(n_layers), 1)
        self.layers = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(d_model, d_model),
                    get_activation(layers_activations, **layer_activations_kwargs),
                )
                for _ in range(n_layers)
            ]
        )
        self.conv_post = nn.Sequential(
            self.get_1d_conv(d_model, d_model, 3, padding=1, norm=norm),
            get_activation(proj_activation, **proj_activation_kwargs),
            nn.BatchNorm1d(d_model),
            self.get_1d_conv(d_model, 1, 1, bias=bias_at_final_layer, norm=norm),
        )
        self.exponential = exponential
        self.n_layers = n_layers
        self.dropout = (
            nn.Identity() if dropout <= 0 or self.n_layers < 2 else nn.Dropout(dropout)
        )
        self.res_sp = 1.0 / ((self.n_layers + 1) * 2)
        self.mask_value = mask_value
        for m in self.conv_post:
            if is_conv(m):
                nn.init.orthogonal_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.weight)
        for m in self.modules():
            if is_conv(m):
                nn.init.xavier_normal_(
                    m.weight,
                    gain=nn.init.calculate_gain(
                        "selu"
                        if layers_activations == "selu"
                        else (
                            "tanh"
                            if layers_activations == "tanh"
                            else (
                                "leaky_relu"
                                if layers_activations in ["leaky_relu", "leakyrelu"]
                                else "conv1d"
                            )
                        )
                    ),
                )
            elif isinstance(m, nn.Linear):
                nn.init.xavier_normal_(
                    m.weight,
                    gain=nn.init.calculate_gain(
                        "selu"
                        if proj_activation == "selu"
                        else (
                            "tanh"
                            if proj_activation == "tanh"
                            else (
                                "leaky_relu"
                                if proj_activation in ["leaky_relu", "leakyrelu"]
                                else "linear"
                            )
                        )
                    ),
                )

    def forward(self, x: Tensor, mask: Optional[Tensor] = None):
        # x=[B, C, d_model]
        if mask is not None:
            x = x.transpose(-1, -2)
            x.masked_fill_(mask, self.mask_value)
            x = x.transpose(-1, -2)

        for layer in self.layers:
            x = self.dropout(x)
            x = layer(x)

        x = x.transpose(-1, -2).contiguous()
        if mask is not None:
            x.masked_fill_(mask, self.mask_value)

        x = self.conv_post(x)

        if self.exponential:
            x = x.exp()
        if self.flatten_outputs:
            x = x.flatten(1, -1)
        return x

    @staticmethod
    def expand_embeddings(x: Tensor, durations: Tensor) -> Tensor:
        """
        Expand per-token embeddings according to predicted or target durations.

        Args:
            x: Tensor of shape [B, seq_len, D] — token embeddings.
            durations: Tensor of shape [B, seq_len] — durations (in frames).

        Returns:
            expanded: Tensor of shape [B, total_frames, D]
                where total_frames = sum(durations[b]) for each batch.
        """
        expanded = []
        durations = torch.clamp(durations, min=1).long()

        for b in range(x.size(0)):
            expanded_seq = torch.repeat_interleave(x[b], durations[b], dim=0)
            expanded.append(expanded_seq)

        # pad to the max total length across the batch for tensor stacking
        max_len = max(seq.size(0) for seq in expanded)
        expanded = [F.pad(seq, (0, 0, 0, max_len - seq.size(0))) for seq in expanded]
        return torch.stack(expanded, dim=0)

    @staticmethod
    def _dur_loss_label(
        durations: Union[List[int], Tensor],
        lengths: Union[List[int], Tensor],  # token lengths
    ):
        """Helper to get the labels for duration loss calculation.

        Args:
            durations (Union[List[int], Tensor]): Expected sizes for unpadded durations
            lengths (Union[List[int], Tensor]): Tokens lengths, same as the durations

        Returns:
            Tensor: Target to be used as loss target for the training process.
        """
        # helper to setup duration loss' label
        mel_lengths = torch.as_tensor(durations, dtype=torch.float32)  # (B,)
        token_lengths = torch.as_tensor(
            lengths, dtype=torch.float32, device=mel_lengths.device
        )  # (B,)
        max_tokens = int(token_lengths.max().item())
        dur_target = torch.zeros(
            mel_lengths.size(-1), max_tokens, device=mel_lengths.device
        )

        for b, (mel_len, tok_len) in enumerate(zip(mel_lengths, token_lengths)):
            # Evenly assign mel frames per token
            avg = mel_len / tok_len
            dur_target[b, : int(tok_len)] = avg

        return dur_target


class AttentionPooling(Model):
    def __init__(self, d_model: int, query_dim: Optional[int] = None):
        super().__init__()
        self.query = nn.Parameter(torch.empty(1, query_dim or d_model))
        self.proj = nn.Linear(d_model, d_model, bias=False)
        nn.init.kaiming_uniform_(self.query, a=math.sqrt(5))

    def forward(self, enc: Tensor, mask: Optional[Tensor] = None):
        # x: [B, N, dim]
        q = self.query.expand(enc.size(0), -1, -1)  # [B, 1, dim]
        attn_scores = torch.matmul(q, self.proj(enc).transpose(-2, -1))  # [B, 1, N]
        if mask is not None:
            attn_scores = attn_scores.masked_fill(mask[:, None, :] == 0, float("-inf"))
        attn_weights = torch.softmax(attn_scores, dim=-1)
        pooled = torch.matmul(attn_weights, enc)  # [B, 1, dim]
        return pooled


class StyleEncoder(Model):
    """
    Audio-only style encoder for TTS.
    Architecture: Conv1D stack → BiGRU → Dense (MLP) → style vector

    Input:
        mel: [B, n_mels, T]  (mel-spectrogram)
    Output:
        style: [B, d_style]  (global style embedding)
    """

    def __init__(
        self,
        n_mels: int = 80,
        d_model: int = 512,
        d_style: int = 256,
        hidden_dim: int = 512,
        kernel_size: int = 5,
        dropout: float = 0.1,
        pooling: Literal["attn", "adaptive"] = "adaptive",
        adaptive_out: int = 1,
        query_dim: Optional[int] = None,
    ):
        super().__init__()

        padding = (kernel_size - 1) // 2
        self.conv = nn.Sequential(
            nn.Conv1d(n_mels, hidden_dim, kernel_size, padding=padding),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv1d(hidden_dim, d_model, kernel_size, padding=padding),
            nn.LeakyReLU(0.1, inplace=True),
        )

        self.mlp = nn.Sequential(
            nn.Linear(d_model, d_model),
            nn.SiLU(),
            nn.Linear(d_model, d_style),
        )

        self.pooling_type = pooling
        if pooling == "adaptive":
            self.pool = nn.AdaptiveAvgPool1d(adaptive_out)
        else:
            self.pool = AttentionPooling(d_model, query_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, mel: Tensor):

        x = self.conv(mel)  # [B, d_model, T]
        x = x.transpose(1, 2)  # [B, T, d_model]

        if self.pooling_type == "adaptive":
            x = x.transpose(-1, -2)  # [B, D, T]
            x = self.pool(x)
            x = x.transpose(-1, -2)  # [B, T, D]
        else:
            x = self.pool(x)  # [B, 1, D]

        x = self.dropout(x)
        style = self.mlp(x)  # [B, 1, d_style]
        return style
