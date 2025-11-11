from __future__ import annotations

from typing import List

from pydantic import BaseModel

from genai_forge import create_llm, PydanticOutputParser
from prompting_forge.prompting import PromptTemplate


class CityPlan(BaseModel):
	city: str
	attractions: List[str]
	days: int


def main() -> None:
	# Prompting comes from prompting-forge; pipes are supported
	template = PromptTemplate(
		system="You are a concise assistant.",
		template="Create a weekend plan.\nCity: {city}",
	)

	llm = create_llm("openai:gpt-4o-mini", temperature=0.2)
	parser = PydanticOutputParser(CityPlan)

	query = "Generate a simple weekend plan for a city."
	chain = query | template | llm | parser
	plan = chain({"city": "Lisbon"})

	print("Parsed plan:")
	print(plan)


if __name__ == "__main__":
	main()
