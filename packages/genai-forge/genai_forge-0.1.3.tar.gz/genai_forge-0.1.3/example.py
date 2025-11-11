from __future__ import annotations

from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

from genai_forge.llm import create_llm
from genai_forge import PydanticOutputParser
from genai_forge.prompting import PromptTemplate


class CityPlan(BaseModel):
    city: str
    attractions: List[str]
    days: int


def main() -> None:
    load_dotenv()

    # Build the chain: query -> prompt template -> llm -> parser
    # The raw user query will be auto-injected if not referenced by {query}.
    template = PromptTemplate(
        system="You are a concise assistant.",
        template="Create a weekend plan.\nCity: {city}",
    )

    llm = create_llm("openai:gpt-4o-mini", temperature=0.2)
    parser = PydanticOutputParser(CityPlan)

    query = "Generate a simple weekend plan for a city."
    chain = query | template | llm | parser
    # Provide only extra variables; query is already embedded at the chain start.
    plan = chain({"city": "Lisbon"})

    print("Parsed plan:")
    print(plan)


if __name__ == "__main__":
    main()


