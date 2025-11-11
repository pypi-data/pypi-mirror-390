from __future__ import annotations

import json
import re
from typing import Any, Dict, Generic, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, ValidationError

TModel = TypeVar("TModel", bound=BaseModel)


class OutputParserException(Exception):
    """Raised when parsing the LLM output fails."""


class BaseOutputParser(Generic[TModel]):
    """
    Base output parser that validates LLM output against a Pydantic model.
    - Provide `get_format_instructions()` to guide the model to emit valid JSON.
    - Provide `parse(text)` to extract/validate JSON into the Pydantic model.
    """

    def __init__(
        self,
        model: Type[TModel],
        *,
        strict: bool = True,
    ) -> None:
        self._model_type = model
        self._strict = strict

    def get_format_instructions(self) -> str:
        """
        Return instructions to include in prompts so the model emits parseable JSON.
        """
        schema = self._model_type.model_json_schema()
        return (
            "Return ONLY valid JSON, with no extra commentary or code fences.\n"
            "The JSON must conform to this schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )

    # Convenience alias used in some frameworks
    format_instructions = get_format_instructions

    def parse(self, text: str) -> TModel:
        """
        Parse and validate the text into the target Pydantic model instance.
        Accepts tolerant inputs: may contain surrounding text or code fences.
        """
        json_obj = self._extract_json(text)
        try:
            return self._model_type.model_validate(json_obj)
        except ValidationError as e:
            if self._strict:
                raise OutputParserException(f"Validation failed: {e}") from e
            # Non-strict: attempt field-level coercion by dumping/loads again.
            try:
                as_json = json.loads(json.dumps(json_obj))
                return self._model_type.model_validate(as_json)
            except Exception as e2:
                raise OutputParserException(f"Coercion failed: {e2}") from e2

    # ---------- internal helpers ----------
    _FENCE_RE = re.compile(r"^```(?:json)?\s*([\s\S]*?)\s*```$", re.IGNORECASE)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract a JSON object from the model output.
        Strategy:
          1) Trim and strip common markdown JSON code-fences.
          2) Try json.loads directly.
          3) Fallback: find the first balanced {...} block and parse it.
        """
        candidate = text.strip()

        # 1) Try to unwrap fenced code blocks ─ e.g. ```json { ... } ```
        fenced = self._maybe_unwrap_fence(candidate)
        if fenced is not None:
            candidate = fenced

        # 2) Direct attempt
        try:
            loaded = json.loads(candidate)
            if isinstance(loaded, dict):
                return loaded
        except Exception:
            pass

        # 3) Fallback: find balanced JSON object
        obj_str = self._find_first_balanced_object(candidate)
        if obj_str is None:
            raise OutputParserException("No JSON object found in output.")
        try:
            loaded = json.loads(obj_str)
            if isinstance(loaded, dict):
                return loaded
        except Exception as e:
            raise OutputParserException(f"Invalid JSON content: {e}") from e
        raise OutputParserException("Parsed JSON is not an object.")

    def _maybe_unwrap_fence(self, text: str) -> Optional[str]:
        m = self._FENCE_RE.match(text)
        if m:
            return m.group(1).strip()
        return None

    def _find_first_balanced_object(self, text: str) -> Optional[str]:
        """
        Find the first balanced {...} substring. Handles nested braces and ignores
        braces inside string literals (simple heuristic).
        """
        start = -1
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            else:
                if ch == '"':
                    in_string = True
                    continue
                if ch == "{":
                    if depth == 0:
                        start = i
                    depth += 1
                elif ch == "}":
                    if depth > 0:
                        depth -= 1
                        if depth == 0 and start != -1:
                            return text[start : i + 1]
        return None


class PydanticOutputParser(BaseOutputParser[TModel]):
    """
    Concrete parser. Alias of BaseOutputParser for clarity/ergonomics.
    """

    def __init__(self, model: Type[TModel], *, strict: bool = True) -> None:
        super().__init__(model=model, strict=strict)



