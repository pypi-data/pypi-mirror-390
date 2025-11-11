# prompting-forge

Minimal, focused prompting library for the Tool-Forge ecosystem.

This package provides the core prompt primitives only:
- `PromptTemplate`: define structured prompts with `{variables}`
- `ChatPrompt`: rendered prompt as messages (system + user)

All LLM execution, chaining, and parsing utilities live in `genai-forge`.

## Install

```bash
pip install prompting-forge
```

For chaining (`query | template | llm | parser`) and model calls:
```bash
pip install genai-forge
```

Python 3.10+.

## Quickstart (with genai-forge)

```python
from prompting_forge.prompting import PromptTemplate
from genai_forge import create_llm, PydanticOutputParser
from pydantic import BaseModel

class CityPlan(BaseModel):
    city: str
    attractions: list[str]
    days: int

template = PromptTemplate(
    system="You are a concise assistant.",
    template="Create a weekend plan.\nCity: {city}",
)

llm = create_llm("openai:gpt-4o-mini", temperature=0.2)
parser = PydanticOutputParser(CityPlan)

query = "Generate a simple weekend plan for a city."
chain = query | template | llm | parser
plan = chain({"city": "Lisbon"})
print(plan)
```

## Notes
- `PromptTemplate` uses Python `str.format`. Missing variables raise clear errors.
- When used with `genai-forge`, parser instructions can be appended automatically.
- The pipe operators on `PromptTemplate` are enabled via a lazy import of `genai_forge.chain`. If you don’t install `genai-forge`, you can still call `template.format(...)` manually and pass the result to your own client.
