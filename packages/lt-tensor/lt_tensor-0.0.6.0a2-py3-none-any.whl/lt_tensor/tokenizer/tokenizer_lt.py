__all__ = ["TokenizerLT"]
from lt_utils.file_ops import (
    is_path_valid,
    find_files,
    is_pathlike,
    save_json,
    load_json,
)
from lt_utils.common import *
import torch
from torch import Tensor
from functools import lru_cache
from torch.nn import functional as F
from lt_utils.type_utils import is_str

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.implementations import ByteLevelBPETokenizer

from .utils import get_full_phonetic_tokens, get_default_tokens
from lt_utils.misc_utils import updateDict, filter_kwargs, default


def get_special_tokens():
    return {
        "pad": "<pad>",
        "unk": "<unk>",
        "sep": "<sep>",
        "bos": "<s>",
        "eos": "</s>",
        "mask": "<mask>",
        "cls": "<cls>",
    }


def _check_special(**special_kws):
    pad = special_kws.get("pad")
    unk = special_kws.get("unk")
    bos = special_kws.get("bos")
    eos = special_kws.get("eos")
    mask = special_kws.get("mask")
    _sep = special_kws.get("sep")
    _cls = special_kws.get("cls")
    special_kws.update(
        {
            "pad": pad if is_str(pad, True, True, False) else "<pad>",
            "unk": unk if is_str(unk, True, True, False) else "<unk>",
            "bos": bos if is_str(bos, True, True, False) else "<s>",
            "eos": eos if is_str(eos, True, True, False) else "</s>",
            "sep": _sep if is_str(_sep, True, True, False) else "<sep>",
            "mask": mask if is_str(mask, True, True, False) else "<mask>",
            "cls": _cls if is_str(_cls, True, True, False) else "<cls>",
        }
    )
    return special_kws


def create_tokenizer(
    tokens: List[str] = get_default_tokens(),
    merges: List[str] = [],
    reserved_tokens: int = 0,
    special_tokens: Dict[str, str] = {
        "pad": "<pad>",
        "unk": "<unk>",
        "sep": "<sep>",
        "bos": "<s>",
        "eos": "</s>",
        "mask": "<mask>",
        "cls": "<cls>",
    },
    byte_fallback: bool = False,
    use_default_decoder: Optional[bool] = None,
    tokenizer_type: Literal["bpe", "byte-level-bpe"] = "bpe",
    *,
    ret_lt: bool = True,
    **tokenizer_kwargs,
):
    assert tokenizer_type in [
        "bpe",
        "byte-level-bpe",
    ], f'Invalid "tokenizer_type": {tokenizer_type}'

    # fist add reserved tokens
    if reserved_tokens > 0:
        for i in range(reserved_tokens):
            tokens.insert(0, f"<|reserved_{i}|>")

    special_tokens = _check_special(**special_tokens.copy()).copy()
    all_special = list(special_tokens.values())

    for s_t in reversed(all_special):
        if s_t not in tokens:
            tokens.insert(0, s_t)

    vocab = {}
    for i, token in enumerate(tokens):
        vocab[token] = i
    if tokenizer_type == "bpe":
        if tokenizer_kwargs:
            tokenizer_kwargs = filter_kwargs(
                BPE,
                False,
                ["vocab", "merges", "byte_fallback"],
                **tokenizer_kwargs.copy(),
            )
        tokenizer_kwargs["unk_token"] = special_tokens.get("unk", "<unk>") or "<unk>"
        tokenizer = Tokenizer(
            BPE(
                vocab=vocab,
                merges=merges,
                byte_fallback=byte_fallback,
                **tokenizer_kwargs,
            )
        )
    else:
        if tokenizer_kwargs:
            tokenizer_kwargs = filter_kwargs(
                ByteLevelBPETokenizer,
                False,
                ["vocab", "merges"],
                **tokenizer_kwargs.copy(),
            )
        tokenizer = ByteLevelBPETokenizer(
            vocab=vocab, merges=merges, **tokenizer_kwargs
        )
    if ret_lt:
        return TokenizerLT(tokenizer, special_tokens, use_default_decoder)
    return tokenizer, special_tokens


class TokenizerLT:

    @property
    def vocab_size(self):
        return self.tokenizer.get_vocab_size()

    @property
    def vocab(self):
        return self.tokenizer.get_vocab()

    def __init__(
        self,
        tokenizer: Union[Tokenizer, str, Path],
        special_tokens: Dict[str, str] = {
            "pad": "<pad>",
            "unk": "<unk>",
            "sep": "<sep>",
            "bos": "<s>",
            "eos": "</s>",
            "mask": "<mask>",
            "cls": "<cls>",
        },
        use_default_decoder: Optional[bool] = None,
    ):
        self.unk_text = ""
        self.special_ids: List[int] = []
        if isinstance(tokenizer, (str, Path)):
            self.load_from_file(tokenizer)
            save_location = None
        else:
            if isinstance(tokenizer, (Tokenizer, ByteLevelBPETokenizer)):
                self.tokenizer: Tokenizer = tokenizer
            else:
                print("No tokenizer has been provided! Creating a new one")
                self.tokenizer, special_tokens = create_tokenizer(
                    special_tokens=special_tokens, ret_lt=False
                )
                print("Dont forget to save it: `tokenizer.save_tokenizer(path)")

            self._setup_special_tokens(**special_tokens)

        self.use_default_decoder = default(
            use_default_decoder,
            (False if isinstance(tokenizer, (Tokenizer, BPE)) else True),
        )

    def __len__(self):
        return self.vocab_size

    def reset_decoder_cache(self):
        self._dec_id.cache_clear()

    def token_to_id(self, token: str) -> int:
        return self.tokenizer.token_to_id(token)

    def id_to_token(self, token: int) -> str:
        return self.tokenizer.id_to_token(token)

    def __call__(
        self,
        texts_or_tokens: Union[str, List[Union[int, str]], Tensor],
        **kwargs,
    ):
        assert isinstance(
            texts_or_tokens, (list, tuple, str, Tensor)
        ), f"invalid input: {texts_or_tokens}"
        source = None
        if isinstance(texts_or_tokens, str):
            return self.encode(texts_or_tokens, **kwargs)
        if isinstance(texts_or_tokens, Tensor):
            return self.decode(texts_or_tokens, **kwargs)
        if isinstance(texts_or_tokens, (list, tuple)):
            if not texts_or_tokens:
                return None
            if all([isinstance(x, int) for x in texts_or_tokens]):
                return self.encode(texts_or_tokens, **kwargs)
            elif all([isinstance(x, str) for x in texts_or_tokens]):
                return self.decode(texts_or_tokens, **kwargs)
        raise ValueError(f"Cannot process texts_or_tokens: '{texts_or_tokens}'")

    def encode(
        self,
        texts: Union[str, List[str]],
        truncation: Union[bool, str, None] = None,
        max_size: Optional[int] = None,
        truncation_direction: Literal["left", "right"] = "left",
        padding_from: Literal["left", "right"] = "right",
        add_bos_token: bool = False,
        add_eos_token: bool = False,
        add_special_tokens: bool = True,
        **kwargs,
    ) -> Union[Tensor, List[Tensor]]:

        assert isinstance(
            texts, (list, tuple, str)
        ), f"Invalid type for texts: '{type(texts)}'. Use either string, or a list of strings."
        if not texts:
            return None

        _kw_unit = dict(
            max_size=max_size if truncation else None,
            truncation=truncation_direction,
            add_bos_token=add_bos_token,
            add_eos_token=add_eos_token,
            add_special_tokens=add_special_tokens,
        )

        was_item_list_format = False
        if isinstance(texts, (list, tuple)):
            assert all(
                list(map(lambda x: isinstance(x, str), texts))
            ), f"All items in the text sequence should be a string, but received: {texts}"
            if len(texts) == 1:
                was_item_list_format = True
                texts = texts[0]

        if isinstance(texts, str):
            result = self._enc(texts, **_kw_unit).view(1, -1)
            if was_item_list_format:
                return [result]
            return result

        tokens = [self._enc(x, **_kw_unit) for x in texts]
        B = len(tokens)
        return self.pad(
            tokens,
            from_left=padding_from == "left",
            to_size=max_size,
        ).view(B, -1)

    def decode(
        self,
        tokenized: Union[int, list[Tensor], List[int], Tensor],
        return_special_tokens: bool = False,
        **kwargs,
    ):
        B = 1
        tok_kwargs = dict(return_special_tokens=return_special_tokens)

        if isinstance(tokenized, Tensor):
            B = tokenized.size(0) if tokenized.ndim > 1 else 1
        elif isinstance(tokenized, int):
            return self.id_to_token(tokenized)
        elif isinstance(tokenized, (list, tuple)):
            if not tokenized:
                return None
            if isinstance(tokenized[0], Tensor):
                assert all(
                    list(map(lambda x: isinstance(x, Tensor), tokenized))
                ), "Not all items provided in the list is a valid tensor"
                B = len(tokenized)
                if B == 1:
                    tokenized = tokenized[0]
            else:
                assert all(
                    list(map(lambda x: isinstance(x, int), tokenized))
                ), "Not all items provided in the list is a valid token"

        if B == 1:
            return self._decode(tokenized, **tok_kwargs)
        return [self._decode(tokenized[i], **tok_kwargs) for i in range(B)]

    def pad(
        self,
        input_ids: list[Tensor],
        from_left: bool = False,
        to_size: Optional[int] = None,
    ):
        assert input_ids, "No value has been provided!"
        if len(input_ids) > 1:
            largest_text = max([x.size(-1) for x in input_ids])
            if to_size:
                largest_text = max(largest_text, to_size)
            if from_left:
                fn = lambda x: (largest_text - x.size(-1), 0)
            else:
                fn = lambda x: (0, largest_text - x.size(-1))
        else:
            if not to_size or to_size <= input_ids[0].shape[-1]:
                return input_ids[0].view(1, input_ids[0].shape[-1])
            if from_left:
                fn = lambda x: (to_size - x.size(-1), 0)
            else:
                fn = lambda x: (0, to_size - x.size(-1))
            return F.pad(
                input_ids[0],
                pad=fn(input_ids[0]),
                mode="constant",
                value=self.pad_token_id,
            ).view(1, to_size)
        B = len(input_ids)
        return torch.stack(
            [
                F.pad(
                    x,
                    pad=fn(x),
                    mode="constant",
                    value=self.pad_token_id,
                )
                for x in input_ids
            ],
            dim=0,
        ).view(B, largest_text)

    def _encode_output_processor(self, output: List[int]):
        return torch.tensor([output], dtype=torch.long)

    @lru_cache(maxsize=65536)
    def _dec_id(self, token: int):
        return self.id_to_token(token) or ""

    def _enc(
        self,
        text: str,
        max_size: Optional[int] = None,
        truncation: Literal["left", "right"] = "left",
        add_bos_token: bool = False,
        add_eos_token: bool = False,
        add_special_tokens: bool = True,
        **kwargs,
    ):
        tokens: List[int] = self.tokenizer.encode(
            text, add_special_tokens=add_special_tokens
        ).ids
        _length = len(tokens)
        if max_size is not None and max_size > 0:
            max_size = max(max_size - int(add_bos_token) - int(add_eos_token), 1)
            if truncation and _length > max_size:
                if truncation == "left":
                    tokens = tokens[-max_size:]
        if add_bos_token:
            tokens.insert(0, self.bos_token_id)
        if add_eos_token:
            tokens.append(self.eos_token_id)
        return torch.tensor([tokens], dtype=torch.long)

    def _decode(
        self,
        tokens: Union[List[int], Tensor],
        return_special_tokens: bool = False,
    ):
        if isinstance(tokens, Tensor):
            tokens = tokens.flatten().tolist()
        if not return_special_tokens:
            tokens = [token for token in tokens.copy() if token not in self.special_ids]
        if self.use_default_decoder:
            return self.tokenizer.decode(tokens, skip_special_tokens=False)
        return "".join([self._dec_id(tok) for tok in tokens if isinstance(tok, int)])

    def load_from_file(self, path: Union[str, Path]):
        is_path_valid(path, validate=True)
        path = Path(path)
        if path.is_file():
            path = path.parent
        # file names
        tokenizer_file = "tokenizer.json"
        config_file = "tokenizer_config.json"
        special_token_map_file = "special_token_map.json"

        self.tokenizer = Tokenizer.from_file(str(path / tokenizer_file))
        special_tokens = load_json(path / special_token_map_file, {})
        settings = load_json(path / config_file, {})
        self.use_default_decoder = settings.get("use_default_decoder", False)
        self._setup_special_tokens(**special_tokens)

    def save_tokenizer(self, path: Union[str, Path]):
        is_pathlike(path, check_if_empty=False, validate=True)
        path = Path(path)
        if "." in path.name:
            path = path.parent
        path.mkdir(exist_ok=True, parents=True)
        self.tokenizer.save(str(path / "tokenizer.json"))
        save_json(
            str(path / "tokenizer_config.json"),
            {"use_default_decoder": self.use_default_decoder},
        )
        save_json(path / "special_token_map.json", self.special_tokens)

    def add_tokens(self, tokens: List[str]):
        self.tokenizer.add_tokens(tokens)

    def add_special_tokens(self, tokens: List[str]):
        self.tokenizer.add_special_tokens(tokens)

    def _setup_special_tokens(self, **kwargs):
        self.special_tokens: Dict[str, int] = {}

        clear_kwargs = _check_special(**kwargs.copy())
        main_tokens = ["pad", "unk", "bos", "mask", "eos", "cls", "sep"]
        for name, token in clear_kwargs.items():
            current = self.tokenizer.token_to_id(token)
            if current is None:
                self.tokenizer.add_tokens([token])
                current = self.tokenizer.token_to_id(token)
            self.tokenizer.add_special_tokens([token])
            self.special_ids.append(current)
            if name in main_tokens:
                updateDict(self, {f"{name}_token_id": current})
            self.special_tokens[f"{name}"] = current
        self._dec_id.cache_clear()
