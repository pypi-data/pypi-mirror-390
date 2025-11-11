# genai-forge

Lightweight utilities to call LLMs and parse their outputs with Pydantic.

## Installation

Install from PyPI:

```bash
pip install genai-forge
```

## Requirements

- Python 3.10+
- An OpenAI API key in your environment:
  - Create a `.env` file at your project root with:

```bash
OPENAI_API_KEY=sk-...
```

`genai_forge` will load `.env` automatically via `python-dotenv` when using the OpenAI provider.

## Quick start

```python
from genai_forge.llm import create_llm
from genai_forge.prompting import PromptTemplate

template = PromptTemplate(
    system="You are a concise expert assistant.",
    template="Generate one actionable tip.\nAudience: {audience}\nTime: {time}",
)

llm = create_llm("openai:gpt-4o-mini", temperature=0.2)

# Chain: query | template | llm
query = "Provide a short productivity tip."
chain = query | template | llm
print(chain({"audience": "Backend Python developer", "time": "30 minutes"}))
```

## Parsing structured outputs with Pydantic

Use `PydanticOutputParser` to have the LLM return valid JSON that is validated into a Pydantic model. When you add a parser to the chain, the parser’s format instructions are automatically appended to the prompt; you do not need to place `{instructions}` in your template.

```python
from typing import List
from pydantic import BaseModel
from genai_forge.llm import create_llm
from genai_forge import PydanticOutputParser
from genai_forge.prompting import PromptTemplate

class CityPlan(BaseModel):
    city: str
    attractions: List[str]
    days: int

template = PromptTemplate(
    system="You are a helpful travel planner.",
    template="Create a city plan.\nCity: {city}\nDays: {days}",
)

llm = create_llm("openai:gpt-4o-mini", temperature=0.1)
parser = PydanticOutputParser(CityPlan)

# Chain: query | template | llm | parser
query = "Create a 2-day city plan for Kyoto."
chain = query | template | llm | parser
result = chain({"city": "Kyoto", "days": 2})  # -> CityPlan
print(result)
```

### What chaining does

The `|` operator builds a Chain:
- `template | llm` produces a function that formats the prompt (system + user) and calls the LLM.
- `template | llm | parser` also injects the parser's format instructions automatically into the prompt and validates the output.

## Output parser: how it works

`PydanticOutputParser`:
- Accepts tolerant output formats (e.g., extra text or ```json fences).
- Extracts JSON from the text (tries direct parse, then finds the first balanced `{...}` block).
- Validates the JSON against your Pydantic model.
- Provides `get_format_instructions()`; the Chain appends it for you when a parser is present.

API surface:

```python
from genai_forge import PydanticOutputParser, BaseOutputParser, OutputParserException
```

Key methods:
- `get_format_instructions() -> str`: Include in your prompt.
- `parse(text: str) -> BaseModel`: Parse and validate output.

## Provider configuration

By default, models without an explicit provider use `openai`. You can specify:

```python
create_llm("openai:gpt-4o-mini")
# or
create_llm("gpt-4.1", provider="openai")
```

The OpenAI provider reads the key from `OPENAI_API_KEY` (or `api_key` argument).

## Running the example

An `example.py` is included at the repo root. It demonstrates:
- A chain: user input → PromptTemplate (with system prompt) → LLM → PydanticOutputParser
- Automatic format instructions injection

Ensure you have a `.env` with `OPENAI_API_KEY`, then:

```bash
python example.py
```

## License

See `LICENSE`.