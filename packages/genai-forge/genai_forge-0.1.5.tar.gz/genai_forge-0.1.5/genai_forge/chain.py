from __future__ import annotations

from typing import Any, Dict, List, Optional

from .parsing import BaseOutputParser
from prompting_forge.prompting import PromptTemplate, ChatPrompt


class Chain:
    """
    Sequential executor for prompt -> llm -> parser compositions.
    Auto-injects parser format instructions into the prompt template if a parser
    is present as the final step.
    """

    def __init__(self, steps: List[Any]) -> None:
        self._steps = steps

    def __or__(self, other: Any) -> "Chain":
        return Chain(self._steps + [other])

    def __call__(self, user_input: Optional[Any] = None) -> Any:
        steps = list(self._steps)

        # Support a leading embedded input value if the chain was started with `query | ...`
        initial_input = None
        if steps and isinstance(steps[0], _InputValue):
            initial_input = steps.pop(0).value

        # Resolve current input by merging initial embedded input with provided input
        current: Any
        if user_input is None:
            current = initial_input
        else:
            if isinstance(initial_input, dict) and isinstance(user_input, dict):
                merged: Dict[str, Any] = {**initial_input, **user_input}
                current = merged
            else:
                current = user_input
        parser: Optional[BaseOutputParser] = None
        if steps and isinstance(steps[-1], BaseOutputParser):
            parser = steps[-1]

        instructions: Optional[str] = None
        if parser is not None:
            instructions = parser.get_format_instructions()

        current: Any = user_input
        for idx, step in enumerate(steps):
            if isinstance(step, PromptTemplate):
                current = step(current, instructions=instructions)
                continue

            # LLM-like step: expects ChatPrompt or str; returns str
            # Delay parsing to parser step only
            if hasattr(step, "__call__") and not isinstance(step, BaseOutputParser):
                current = step(current)
                continue

            if isinstance(step, BaseOutputParser):
                current = step.parse(str(current))
                continue

            raise TypeError(f"Unsupported chain step at index {idx}: {type(step)}")

        return current


def to_chain(left: Any, right: Any) -> Chain:
    """
    Helper: combine two steps into a chain.
    """
    left_chain = left if isinstance(left, Chain) else Chain([left])
    return left_chain | right


class _InputValue:
    """
    Internal step to embed an initial input value into a chain, enabling
    expressions like: `query | template | llm | parser`.
    """

    def __init__(self, value: Any) -> None:
        self.value = value



