from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ChatPrompt:
	"""
	Minimal chat prompt representation.
	"""
	system: Optional[str]
	user: str

	def to_messages(self) -> list[dict]:
		messages: list[dict] = []
		if self.system:
			messages.append({"role": "system", "content": self.system})
		messages.append({"role": "user", "content": self.user})
		return messages


class PromptTemplate:
	"""
	Simple Python format-based prompt template with a single system prompt string,
	and a user template string.
	"""

	def __init__(self, *, system: Optional[str], template: str) -> None:
		self._system = system
		self._template = template

	def __or__(self, other: Any):
		# Lazy import to avoid hard install-time dependency
		from genai_forge.chain import Chain  # type: ignore
		return Chain([self]) | other

	def __ror__(self, left: Any):
		"""
		Enable chaining from a raw query or variables dictionary:
		  "some question" | template | llm | parser
		"""
		from genai_forge.chain import Chain, _InputValue  # type: ignore
		return Chain([_InputValue(_normalize_left(left)), self])

	def format(self, variables: Any, *, instructions: Optional[str] = None) -> ChatPrompt:
		"""
		Format the template with variables. If variables is not a mapping, it will
		be available as the 'input' variable. If instructions are provided, they
		are appended to the user content automatically.
		"""
		context: Dict[str, Any]
		if isinstance(variables, dict):
			context = dict(variables)
		else:
			# Treat raw input as the user's query
			context = {"query": variables}

		user_text = self._template.format(**context)

		# Ensure the raw user query is present even if not in the template
		if "query" in context and "{query}" not in self._template:
			q = str(context["query"]).strip()
			if q:
				if user_text.strip():
					user_text = f"{user_text.rstrip()}\n\n{q}"
				else:
					user_text = q

		# Automatically include parser instructions if present
		if instructions:
			user_text = f"{user_text.rstrip()}\n\n{instructions}"

		return ChatPrompt(system=self._system, user=user_text)

	def __call__(self, variables: Any, *, instructions: Optional[str] = None) -> ChatPrompt:
		return self.format(variables, instructions=instructions)


def _normalize_left(left: Any) -> Any:
	"""
	Normalize left operand value when starting a chain with `query | template`.
	- str -> {"query": str}
	- dict -> dict (unchanged)
	- other -> {"query": str(value)}
	"""
	if isinstance(left, dict):
		return left
	if isinstance(left, str):
		return {"query": left}
	return {"query": str(left)}


