from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from prompting_forge.prompting import PromptTemplate
from prompting_forge.versioning import (
	save_prompt_version,
	list_prompt_versions,
	load_final_prompt,
	save_final_prompt,
)


class LLMCall:
	"""
	LLM executor that can optionally version prompts and synthesize a final prompt.
	- Prompt rendering is done via prompting-forge's PromptTemplate.
	- Prompt versioning and final prompt storage are delegated to prompting-forge.
	"""

	def __init__(self, name: str, client: Any, *, enable_versioning: bool = False, version_root: Path | None = None) -> None:
		self._name = name.strip()
		if not self._name:
			raise ValueError("LLMCall name cannot be empty")
		self._client = client
		self._enable_versioning = bool(enable_versioning)
		self._version_root = version_root

	def run(self, prompt_template: PromptTemplate, context: Dict[str, Any]) -> Tuple[str, str]:
		if not isinstance(context, dict):
			raise TypeError("context must be a dict")

		# If template requests a final prompt, ensure one exists (synth or load)
		if getattr(prompt_template, "wants_final_prompt", None) and prompt_template.wants_final_prompt():
			final_data = load_final_prompt(self._name, root=self._version_root)
			if final_data is None:
				final_data = self._synthesize_final_prompt()
				save_final_prompt(self._name, system=final_data.get("system"), template=final_data["template"], notes=final_data.get("notes"), root=self._version_root)
			# Use synthesized final template (system + user template)
			prompt_template = PromptTemplate(
				system=final_data.get("system"),
				template=final_data["template"],
			)

		# Important: template must NOT embed parser format instructions.
		rendered = prompt_template.render(context, strict=True)

		if self._enable_versioning:
			save_prompt_version(self._name, rendered, root=self._version_root)

		response = self._execute(rendered)
		return rendered, response

	def _synthesize_final_prompt(self) -> Dict[str, Any]:
		"""
		Ask the LLM to propose an improved system/template based on history.
		Output format:
		{
			"system": "... or null",
			"template": "must not include parser format instructions",
			"notes": "rationale"
		}
		"""
		history_files = list_prompt_versions(self._name, root=self._version_root)
		history_texts: List[str] = []
		for p in history_files[-10:]:  # last 10 versions
			try:
				history_texts.append(p.read_text(encoding="utf-8"))
			except Exception:
				pass

		instructions = (
			"You are refining a prompt across multiple iterations. "
			"Given prior rendered prompts (which may include system text, user template, and formatting hints), "
			"produce a clean, high-quality prompt split into two fields:\n"
			'{"system": string|null, "template": string, "notes": string}. '
			"The 'template' must contain only the user-facing content with placeholders as needed (e.g., {city}, {days}). "
			"Do NOT include any output parser format instructions or JSON schemas in 'template'. "
			"Keep 'system' concise; use null if not needed. "
			"Explain changes briefly in 'notes'."
		)

		joined = "\n\n---\n\n".join(history_texts) if history_texts else "No prior versions."
		prompt = f"{instructions}\n\n# Prior versions:\n{joined}\n\n# Return ONLY a JSON object."
		raw = self._execute(prompt)
		try:
			data = json.loads(raw)
			if not isinstance(data, dict) or "template" not in data:
				raise ValueError("invalid")
			return {"system": data.get("system"), "template": data["template"], "notes": data.get("notes", "")}
		except Exception:
			# Fallback minimal template
			return {"system": None, "template": "Write a helpful response to: {query}", "notes": "fallback"}

	def _execute(self, rendered_text: str) -> str:
		client = self._client
		# Duck-typed call: callable client returns str
		result = client(rendered_text) if callable(client) else rendered_text
		return str(result)


