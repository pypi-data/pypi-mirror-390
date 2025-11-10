__all__ = [
    "TextEmbeddings",
    "TextEncoderLSTM",
    "TextEncoderLSTMConfig",
    "MultiHeadSelfAttention",
    "TransformerEncoderLayer",
    "TextEncoderTransformer",
    "TextEncoderAttnLSTM",
]

from lt_utils.common import *
from lt_tensor.common import *
from lt_tensor.activations_utils import get_activation, ACTIV_NAMES_TP

from lt_tensor.model_zoo.pos_encoders import (
    RotaryPositionalEncoding,
    SinusoidalPositionalEncoding,
)
from lt_tensor.model_zoo.conv_norm import Conv1dNorm, ConvNormConfig


class TextEmbeddings(Model):
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 256,
        position_encoder_type: Optional[
            Literal[
                "absolute",
                "sinusoidal",
                "rotary",
            ]
        ] = "sinusoidal",
        max_seq_len: int = 2048,
        rotary_base: int = 10000,
        rotary_dim: Optional[int] = None,
        rotary_reshape: bool = True,
        padding_idx: Optional[int] = None,
        transposed_output: bool = False,
        *,
        max_norm: Optional[float] = None,
        norm_type: float = 2,
        scale_grad_by_freq: bool = False,
        sparse: bool = False,
    ):
        super().__init__()
        self.embedding = nn.Embedding(
            vocab_size,
            d_model,
            padding_idx=padding_idx,
            max_norm=max_norm,
            norm_type=norm_type,
            scale_grad_by_freq=scale_grad_by_freq,
            sparse=sparse,
        )
        self.position_encoder_type: Optional[
            Literal["absolute", "sinusoidal", "rotary"]
        ] = position_encoder_type
        if self.position_encoder_type is not None:
            if position_encoder_type == "absolute":
                self.pos_emb = nn.Embedding(max_seq_len, d_model)
            elif position_encoder_type == "rotary":
                self.pos_emb = RotaryPositionalEncoding(
                    d_model=d_model,
                    rotary_dim=rotary_dim,
                    base=rotary_base,
                    reshape_output=rotary_reshape,
                )
            else:

                self.pos_emb = SinusoidalPositionalEncoding(
                    d_model=d_model,
                    base=rotary_base or max_seq_len,
                )
        else:
            self.pos_emb = nn.Identity()

        self.transposed_output = transposed_output

    def forward(self, input_ids: Tensor, position_ids: Optional[Tensor] = None):
        """input_ids (long) =  [B, T]"""
        B, T = input_ids.shape
        inputs_embeds = self.embedding(input_ids)  # [B, T, emb]
        if self.position_encoder_type == "absolute":
            if position_ids is None:
                position_ids = (
                    torch.arange(T, device=inputs_embeds.device, dtype=torch.long)
                    .unsqueeze(0)
                    .expand(B, T)
                )
            else:
                position_ids = position_ids.long()
            emb = inputs_embeds + self.pos_emb(position_ids)
        else:
            emb = self.pos_emb(inputs_embeds)

        if self.transposed_output:
            emb = emb.transpose(-1, -2)
        return emb


class TextEncoderLSTMConfig(ModelConfig):
    vocab_size: int = 0
    d_model: int = 256
    cnn_config = ConvNormConfig(
        channels=[256, 256],
        kernel_size=[3, 3],
        dilation=[1, 1],
        stride=[1, 1],
        groups=[1, 1],
        padding=[1, 1],
        activation="gelu",
        norm_bias=False,
    )
    n_layers: int = 2
    lstm_dropout: float = 0.01
    cnn_dropout: float = 0.1
    padding_id: int = 0
    position_encoder_type: Optional[
        Literal[
            "absolute",
            "sinusoidal",
            "rotary",
        ]
    ] = "rotary"
    rotary_base: int = 10000
    rotary_dim: Optional[int] = None
    mask_value: Number = 0.0
    activation: ACTIV_NAMES_TP = "silu"
    activation_kwargs: Dict[str, Any] = dict()

    def __init__(
        self,
        vocab_size: int = 0,
        d_model: int = 256,
        cnn_config: Union[ConvNormConfig, dict] = ConvNormConfig(
            channels=[256, 256],
            kernel_size=[3, 3],
            dilation=[1, 1],
            stride=[1, 1],
            groups=[1, 1],
            padding=[1, 1],
            activation="gelu",
            norm_bias=False,
        ),
        n_layers: int = 2,
        dropout: float = 0.1,
        padding_id: int = 0,
        position_encoder_type: Optional[
            Literal[
                "absolute",
                "sinusoidal",
                "rotary",
            ]
        ] = "rotary",
        cnn_dropout: float = 0.1,
        rotary_base: int = 10000,
        rotary_dim: Optional[int] = None,
        mask_value: Number = 0.0,
        activation: ACTIV_NAMES_TP = "silu",
        activation_kwargs: Dict[str, Any] = dict(),
        crop_larger_configs: bool = True,
        *args,
        **kwargs,
    ):
        if not isinstance(cnn_config, (ConvNormConfig, ModelConfig, dict)):
            raise ValueError(
                f"Invalid `cnn_config` {cnn_config}. Use either ConvNormConfig or a dictionary."
            )
        self.crop_larger_configs = crop_larger_configs
        settings = dict(
            vocab_size=vocab_size,
            d_model=d_model,
            cnn_config=cnn_config,
            n_layers=n_layers,
            cnn_dropout=cnn_dropout,
            dropout=dropout,
            padding_id=padding_id,
            position_encoder_type=position_encoder_type,
            rotary_base=rotary_base,
            rotary_dim=rotary_dim,
            mask_value=mask_value,
            activation=activation,
            activation_kwargs=activation_kwargs,
        )
        super().__init__(**settings)
        self.post_process()

    def post_process(self):
        self.cnn_config = ConvNormConfig(**self.cnn_config)
        items_list = [
            self.cnn_config.channels,
            self.cnn_config.kernel_size,
            self.cnn_config.dilation,
        ]
        sizes = [len(x) for x in items_list]
        min_sizes = min(sizes)
        max_sizes = max(sizes)
        if max_sizes != min_sizes:
            if self.crop_larger_configs:
                self.cnn_config.fix_lists("crop_larger")
            else:
                self.cnn_config.fix_lists("pad_smaller")
        self.cnn_config.dropout = self.cnn_dropout


class TextEncoderLSTM(Model):
    def __init__(self, config: Union[TextEncoderLSTMConfig, Dict[str, Any]]):
        super().__init__()
        if not isinstance(config, (TextEncoderLSTMConfig, ModelConfig)):
            assert isinstance(
                config, dict
            ), "Invalid type for config: {config}. use either a dictionary or TextEncoderConfig or a ModelConfig"
            config = TextEncoderLSTMConfig(**config)
        assert config.vocab_size > 0, "Vocab size cannot be zero or negative values!"
        self.cfg = config

        self.embedding = TextEmbeddings(
            vocab_size=config.vocab_size,
            d_model=config.d_model,
            position_encoder_type=config.position_encoder_type,
            padding_idx=config.padding_id,
            rotary_reshape=True,
            rotary_base=config.rotary_base,
            rotary_dim=config.rotary_dim,
        )
        self.mask_value = config.mask_value
        self.cnn = nn.ModuleList()

        self.cnn_cfg = config.cnn_config
        self.apply_mask_at_output = config.apply_mask_at_output
        config.cnn_config.fix_lists("crop_larger")
        self.cnn_layers = len(config.cnn_config)
        for i in range(self.cnn_layers):
            self.cnn.append(Conv1dNorm(self.cnn_cfg, config.d_model, i))

        self.rnn = nn.LSTM(
            config.cnn_config.channels[-1],
            config.d_model,
            num_layers=config.n_layers,
            dropout=0 if config.n_layers < 2 else config.lstm_dropout,
            batch_first=True,
            bidirectional=True,
        )
        self.proj_out: Callable[[Tensor], Tensor] = nn.Sequential(
            get_activation(config.activation, **config.activation_kwargs),
            nn.Linear(config.d_model * 2, config.d_model),
        )

    def rnn_pass(
        self,
        x: Tensor,
        B: int,
        T: int,
        lengths: List[int] = None,
        mask: Optional[Tensor] = None,
    ) -> Tensor:
        if mask is not None:
            x = x.transpose(-1, -2)
            x.masked_fill_(mask, self.mask_value)
            x = x.transpose(-1, -2)
        if lengths is None:
            lengths = [T for _ in range(B)]
        elif isinstance(lengths, Tensor):
            lengths = lengths.clone().detach().cpu().long().tolist()

        packed = nn.utils.rnn.pack_padded_sequence(
            x,
            lengths,
            batch_first=True,
            enforce_sorted=False,
        )
        self.rnn.flatten_parameters()
        out_packed = self.rnn(packed)[0]
        x = nn.utils.rnn.pad_packed_sequence(out_packed, batch_first=True)[0]
        return x

    def cnn_pass(self, x: Tensor, mask: Optional[Tensor] = None) -> Tensor:
        x = x.transpose(-1, -2)  # [B, emb, T]
        for c in self.cnn:
            x = c(x, mask)
        x = x.transpose(-1, -2)
        return x

    def __call__(self, *args, **kwds) -> Tuple[Tensor, Tensor]:
        return super().__call__(*args, **kwds)

    def forward(
        self,
        input_ids: Tensor,
        lengths: List[int] = None,
        mask: Optional[Tensor] = None,
    ):
        B, T = input_ids.size(0), input_ids.size(-1)
        emb: Tensor = self.embedding(input_ids.view(B, T))  # [B, T, emb]
        x = self.cnn_pass(emb, mask)
        x = self.rnn_pass(x, B, T, lengths, mask)

        x = self.proj_out(x)
        x = x.transpose(-1, -2)
        return x, emb


class RotaryPositionalEmbedding(Model):
    def __init__(self, d_model):
        super().__init__()
        self.dim = d_model
        inv_freq = 1.0 / (10000 ** (torch.arange(0, d_model, 2).float() / d_model))
        self.register_buffer("inv_freq", inv_freq)

    def forward(self, seq_len):
        t = torch.arange(seq_len, device=self.inv_freq.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)  # [seq_len, dim/2]
        emb = torch.cat((freqs.sin(), freqs.cos()), dim=-1)
        return emb  # [seq_len, dim]


def apply_rotary_pos_emb(q, k, rotary_emb):
    # q, k: [batch, heads, seq_len, head_dim]
    cos, sin = rotary_emb[..., ::2].cos(), rotary_emb[..., 1::2].sin()
    q1, q2 = q[..., ::2], q[..., 1::2]
    k1, k2 = k[..., ::2], k[..., 1::2]
    q = torch.cat([q1 * cos - q2 * sin, q1 * sin + q2 * cos], dim=-1)
    k = torch.cat([k1 * cos - k2 * sin, k1 * sin + k2 * cos], dim=-1)
    return q, k


class MultiHeadSelfAttention(Model):
    def __init__(
        self,
        d_model: int,
        n_heads: int,
        dropout: float = 0.0,
        proj_bias: bool = False,
    ):
        super().__init__()
        self.num_heads = n_heads
        self.head_dim = d_model // n_heads
        self.scale = self.head_dim**-0.5

        self.qkv = nn.Linear(d_model, d_model * 3, bias=False)
        self.proj = nn.Linear(d_model, d_model, bias=proj_bias)
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: Tensor,
        mask: Optional[Tensor] = None,
        rotary_emb: Optional[Tensor] = None,
    ):
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim)
        q, k, v = qkv[:, :, 0], qkv[:, :, 1], qkv[:, :, 2]  # [B, N, heads, head_dim]
        q = q.permute(0, 2, 1, 3)  # [B, heads, N, head_dim]
        k = k.permute(0, 2, 1, 3)
        v = v.permute(0, 2, 1, 3)

        if rotary_emb is not None:
            rotary_emb = rotary_emb[:N].unsqueeze(0).unsqueeze(0)  # [1,1,seq_len,dim]
            q, k = apply_rotary_pos_emb(q, k, rotary_emb)

        # mask shape expected: [B, 1, N, N] or [B, N, N]
        out = F.scaled_dot_product_attention(
            q, k, v, attn_mask=mask, dropout_p=self.dropout.p if self.training else 0.0
        )
        out = out.permute(0, 2, 1, 3).reshape(B, N, C)
        return self.proj(out)


# -----------------------
# Transformer Encoder Layer
# -----------------------
class TransformerEncoderLayer(Model):
    def __init__(
        self,
        d_model: int = 128,
        n_heads: int = 4,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        norm_bias: bool = False,
        affine: bool = True,
        attn_dropout: float = 0.1,
        attn_bias: bool = False,
    ):
        super().__init__()
        self.attn = MultiHeadSelfAttention(
            d_model, n_heads, dropout=attn_dropout, proj_bias=attn_bias
        )
        self.norm1 = nn.LayerNorm(d_model, bias=norm_bias, elementwise_affine=affine)
        self.norm2 = nn.LayerNorm(d_model, bias=norm_bias, elementwise_affine=affine)
        self.mlp = nn.Sequential(
            nn.Linear(d_model, int(d_model * mlp_ratio)),
            nn.GELU(),
            nn.Linear(int(d_model * mlp_ratio), d_model),
            nn.Dropout(dropout),
        )

    def forward(
        self,
        x: Tensor,
        mask: Optional[Tensor] = None,
        rotary_emb: Optional[Tensor] = None,
    ):
        x = x + self.attn(self.norm1(x), rotary_emb=rotary_emb, mask=mask)
        x = x + self.mlp(self.norm2(x))
        return x


# -----------------------
# Transformer Text Encoder
# -----------------------
class TextEncoderTransformer(Model):
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        n_heads: int = 4,
        n_layers: int = 4,
        mlp_ratio: float = 4.0,
        dropout: float = 0.1,
        padding_id: int = 0,
        norm_bias: bool = False,
        affine: bool = True,
        attn_dropout: float = 0.01,
        attn_bias: bool = False,
    ):
        super().__init__()
        self.token_emb = nn.Embedding(vocab_size, d_model, padding_idx=padding_id)
        self.layers = nn.ModuleList(
            [
                TransformerEncoderLayer(
                    d_model,
                    n_heads,
                    mlp_ratio,
                    dropout,
                    norm_bias=norm_bias,
                    attn_bias=attn_bias,
                    attn_dropout=attn_dropout,
                )
                for _ in range(n_layers)
            ]
        )
        self.norm = nn.LayerNorm(d_model, bias=norm_bias, elementwise_affine=affine)
        self.rotary_emb = RotaryPositionalEmbedding(d_model // n_heads)

    def forward(self, x: Tensor, mask: Optional[Tensor] = None):
        N = x.size(-1)
        x = self.token_emb(x)  # [B, N, dim]
        rotary = self.rotary_emb(N)  # [seq_len, head_dim]

        for layer in self.layers:
            x = layer(x, rotary_emb=rotary, mask=mask)

        x = self.norm(x)
        return x


class ResidualConv1DBlock(Model):
    def __init__(
        self,
        d_model: int,
        kernel_size: int = 3,
        dilation: int = 1,
        dropout=0.0,
        eps: float = 1e-5,
        affine: bool = True,
        bias: bool = True,
        activation: ACTIV_NAMES_TP = "leaky_relu",
        activation_kwargs: Dict[str, Any] = dict(negative_slope=0.1),
    ):
        super().__init__()
        self.conv = nn.Conv1d(
            d_model,
            d_model,
            kernel_size=kernel_size,
            dilation=dilation,
            padding=((kernel_size - 1) * dilation) // 2,
            bias=bias,
        )
        self.norm = nn.LayerNorm(d_model, eps=eps, elementwise_affine=affine)
        self.activation = get_activation(activation, **activation_kwargs)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: Tensor):
        # x: [B, N, dim] -> transpose for conv1d
        residual = x
        x = self.conv(x)
        x = x.transpose(1, 2)  # [B, N, dim]
        x = self.norm(x + x)  # residual + layer norm
        x = x.transpose(1, 2)  # [B, dim, N]
        x = self.activation(x)
        x = self.dropout(x)
        return x + residual


class TextEncoderAttnLSTM(Model):
    def __init__(
        self,
        vocab_size: int,
        d_model: int = 128,
        n_heads: int = 4,
        cnn_layers: int = 2,
        n_layers: int = 4,
        residual_kernel: int = 3,
        residual_bias: bool = False,
        attn_dropout: float = 0.01,
        affine: bool = True,
        proj_bias: bool = False,
        padding_id: int = 0,
        attn_bias: bool = False,
    ):
        super().__init__()
        self.attn = MultiHeadSelfAttention(
            d_model, n_heads, attn_dropout, proj_bias=attn_bias
        )
        self.embed = nn.Embedding(vocab_size, d_model, padding_idx=padding_id)
        self.pos_emb = RotaryPositionalEmbedding(d_model // n_heads)

        # CNN loop
        self.cnn = nn.Sequential(
            *[
                ResidualConv1DBlock(
                    d_model,
                    kernel_size=residual_kernel,
                    bias=residual_bias,
                    affine=affine,
                )
                for _ in range(cnn_layers)
            ]
        )

        # Bi-LSTM
        self.rnn = nn.LSTM(
            d_model,
            d_model,
            batch_first=True,
            num_layers=n_layers,
            bidirectional=True,
        )

        self.proj = nn.Linear(d_model * 2, d_model, bias=proj_bias)

    def rnn_pass(
        self,
        x: Tensor,
        B: int,
        T: int,
        lengths: List[int] = None,
        mask: Optional[Tensor] = None,
    ) -> Tensor:
        if mask is not None:
            x = x.transpose(-1, -2)
            x.masked_fill_(mask, self.mask_value)
            x = x.transpose(-1, -2)
        if lengths is None:
            lengths = [T for _ in range(B)]
        elif isinstance(lengths, Tensor):
            lengths = lengths.clone().detach().cpu().long().tolist()

        packed = nn.utils.rnn.pack_padded_sequence(
            x,
            lengths,
            batch_first=True,
            enforce_sorted=False,
        )
        self.rnn.flatten_parameters()
        out_packed = self.rnn(packed)[0]
        x = nn.utils.rnn.pad_packed_sequence(out_packed, batch_first=True)[0]
        return x

    def forward(
        self,
        input_ids: Tensor,
        lengths: List[int] = None,
        mask: Optional[Tensor] = None,
        attn_mask: Optional[Tensor] = None,
    ):
        # x: [B, N]
        x = self.embed(x)  # [B, N, dim]
        rotary = self.pos_emb(x.size(1))
        x = self.attn(x, rotary_emb=rotary, mask=attn_mask)  # [B, N, dim]
        x = x.transpose(1, 2)  # [B, dim, N] for CNN
        x = self.cnn(x)
        x = x.transpose(1, 2)  # back to [B, N, dim]
        x = self.rnn_pass(input_ids, lengths, mask)  # [B, N, 2*hidden]
        x = self.proj(x)  # [B, N, mlp_out_dim]
        return x
