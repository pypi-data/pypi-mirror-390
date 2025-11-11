from __future__ import annotations

import os
from typing import Any, Optional

from dotenv import load_dotenv
from openai import OpenAI

from genai_forge.llm.base import BaseLLM
from genai_forge.llm.registry import register_llm
from prompting_forge.prompting import ChatPrompt


@register_llm("openai")
class OpenAIChatLLM(BaseLLM):
    def __init__(
        self,
        *,
        model: str,
        temperature: float = 0.3,
        api_key: Optional[str] = None,
        logger: Any = None,
    ) -> None:
        load_dotenv()
        key = api_key or os.getenv("OPENAI_API_KEY")
        # Client can also read key from env automatically, but we pass it if present
        self._client = OpenAI(api_key=key) if key else OpenAI()
        self._model = model
        self._temperature = float(temperature)
        self._logger = logger

    def __call__(self, prompt: Any) -> str:
        if isinstance(prompt, ChatPrompt):
            messages = prompt.to_messages()
        else:
            # Fallback: treat as plain user text
            content = self._normalize_prompt(prompt)
            messages = [{"role": "user", "content": content}]
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=messages,  # type: ignore[arg-type]
            temperature=self._temperature,
        )
        message = resp.choices[0].message.content or ""
        return message



