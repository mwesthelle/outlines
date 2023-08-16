from typing import TYPE_CHECKING, Optional

import numpy as np
import torch

from outlines.models.transformers import TransformersTokenizer

if TYPE_CHECKING:
    from ctranslate2 import Generator  # type: ignore
    from transformers import PreTrainedTokenizer


__all__ = ["ctranslate2"]


class CTranslate2:
    """Represents a `ctranslate2` CausalLM."""

    def __init__(
        self,
        model: "Generator",
        tokenizer: "PreTrainedTokenizer",
        device: Optional[str] = None,
    ):
        self.device = device if device is not None else "cpu"
        self.model = model
        self.tokenizer = tokenizer

    def __call__(
        self, input_ids: torch.LongTensor, attention_mask: torch.LongTensor
    ) -> torch.FloatTensor:
        # `forward_batch` method of `Generator` accepts `tokens` in a list of list of str

        tokens = [
            self.tokenizer.tokenizer.convert_ids_to_tokens(iids) for iids in input_ids
        ]
        logits = self.model.forward_batch(tokens, return_log_probs=True)
        if self.device == "cpu":
            # See: https://github.com/OpenNMT/CTranslate2/issues/1386
            logits = np.array(logits)
        logits = torch.as_tensor(logits)
        next_token_logits = logits[:, -1, :]

        return next_token_logits


def ctranslate2(
    ctr2_model: str, tokenizer_name: str, device: Optional[str] = None, **model_kwargs
):
    try:
        from ctranslate2 import Generator
    except ImportError:
        raise ImportError(
            "The `ctranslate2` library needs to be installed in order to use `ctranslate2` models."
        )
    
    model = Generator(ctr2_model, device=device)
    tokenizer = TransformersTokenizer(tokenizer_name, **model_kwargs)

    return CTranslate2(model, tokenizer)
