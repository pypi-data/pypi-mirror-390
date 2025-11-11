from __future__ import annotations

"""
Common LLM interfaces and base class.

Exposes:
  - LLM (Protocol): minimal callable interface.
  - BaseLLM (ABC): enforces __call__ and supports piping with parsers via `|`.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, runtime_checkable

from genai_forge.chain import Chain, to_chain
from prompting_forge.prompting import ChatPrompt
from genai_forge.parsing import BaseOutputParser

@runtime_checkable
class LLM(Protocol):
    """Protocol for any Large Language Model interface."""

    def __call__(self, prompt: Any) -> str: ...


class BaseLLM(ABC):
    """
    Abstract base class for LLMs.
    Responsibilities:
      - Require subclasses to implement `__call__(prompt) -> str`.
      - Provide the `|` operator to compose with a parser/transformer.
    """

    @abstractmethod
    def __call__(self, prompt: Any) -> str:
        """Execute the LLM on the given prompt and return the text output."""
        raise NotImplementedError

    def __or__(self, other: Any) -> Chain:
        """
        Compose into a Chain so we can auto-inject parser instructions and
        support PromptTemplate -> LLM -> OutputParser flows.
        """
        return to_chain(self, other)

    @staticmethod
    def _normalize_prompt(prompt: Any) -> str:
        """
        Normalize a prompt to a plain string.
        If `prompt` has `.to_string()`, it will be used; otherwise `str(prompt)`.
        """
        if hasattr(prompt, "to_string"):
            return str(prompt.to_string())
        # Accept ChatPrompt: convert to string user content (system handled in provider)
        if isinstance(prompt, ChatPrompt):
            # Concatenate system + user text as a plain string fallback
            if prompt.system:
                return f"{prompt.system}\n\n{prompt.user}"
            return prompt.user
        return str(prompt)



