from __future__ import annotations

"""
Provider registry + LLM factory.
Exposes:
  - register_llm(provider: str)
  - create_llm(model: str, **kwargs)
"""

from typing import Any, Callable, Dict, Optional, Tuple

from .base import LLM
from dotenv import load_dotenv

_LLM_REGISTRY: Dict[str, Callable[..., LLM]] = {}


def register_llm(provider: str) -> Callable[[Callable[..., LLM]], Callable[..., LLM]]:
    """
    Decorator to register an LLM provider class or factory.
    Usage:
        @register_llm("openai")
        class OpenAIChatLLM(BaseLLM):
            ...
    """
    prov = provider.lower().strip()

    def _wrap(cls_or_factory: Callable[..., LLM]) -> Callable[..., LLM]:
        _LLM_REGISTRY[prov] = cls_or_factory
        return cls_or_factory

    return _wrap


def create_llm(
    model: str,
    *,
    temperature: float = 0.3,
    api_key: Optional[str] = None,
    provider: Optional[str] = None,
    logger: Any = None,
) -> LLM:
    """
    Factory to create an LLM instance from a model string.
    Args:
        model: Either "provider:model_id" (e.g., "openai:chatgpt-4o")
               or just "model_id" (provider inferred/overridden by `provider`).
        temperature: Sampling temperature.
        system_prompt: Optional system message.
        api_key: Optional explicit key override.
        provider: Optional explicit provider if not in `model`.
        logger: Optional logger.
    Returns:
        An initialized LLM instance.
    Raises:
        ValueError: Unknown/unsupported provider.
    """
    # Ensure environment variables from .env are available for any provider
    load_dotenv()

    prov, model_id = _split_provider_model(model, provider)
    prov_norm = prov.lower().strip()
    factory = _LLM_REGISTRY.get(prov_norm)
    if factory is None:
        raise ValueError(
            f"Unknown LLM provider '{prov_norm}'. Registered: {sorted(_LLM_REGISTRY.keys())}"
        )
    return factory(model=model_id, temperature=temperature, api_key=api_key, logger=logger)


def _split_provider_model(model: str, provider: Optional[str]) -> Tuple[str, str]:
    """
    Split a model string into (provider, model_id).
    Examples:
        "openai:chatgpt-4o" -> ("openai", "chatgpt-4o")
        "gpt-4.1" + provider="openai" -> ("openai", "gpt-4.1")
        "gpt-4.1" (no provider) -> defaults to ("openai", "gpt-4.1")
    """
    if ":" in model:
        p, _, m = model.partition(":")
        return p, m
    if provider:
        return provider, model
    # default provider for bare model strings
    return "openai", model



