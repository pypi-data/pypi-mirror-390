from __future__ import annotations

from dataclasses import dataclass
import string
from typing import Any, Dict, Iterable, Mapping, Optional, Set


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

	def __init__(self, *, system: Optional[str], template: str, variables: Optional[Iterable[str]] = None, create_final_prompt: bool = False) -> None:
		self._system = system
		self._template = template
		self._variables = list(variables) if variables is not None else None
		# When True, LLMCall may synthesize a final prompt from version history if missing
		self._create_final_prompt = bool(create_final_prompt)

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

		self._validate_required_variables(context)

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

	def render(self, context: Mapping[str, Any], *, strict: bool = True) -> str:
		"""
		Render prompt to a plain string. Validates required variables first.
		"""
		if not isinstance(context, Mapping):
			raise TypeError("context must be a mapping of variable names to values")
		if strict:
			self._validate_required_variables(context)  # may raise
		return self._template.format(**context)  # may still KeyError if non-strict

	def wants_final_prompt(self) -> bool:
		return self._create_final_prompt

	def _expected_variables(self) -> Set[str]:
		if self._variables is not None:
			return {str(v) for v in self._variables}
		# Parse placeholders from the template
		fields: Set[str] = set()
		for literal_text, field_name, format_spec, conversion in string.Formatter().parse(self._template):
			if field_name:
				root = field_name.split(".")[0].split("[")[0]
				if root:
					fields.add(root)
		return fields

	def _validate_required_variables(self, context: Mapping[str, Any]) -> None:
		required = self._expected_variables()
		missing = sorted([name for name in required if name not in context])
		if missing:
			raise ValueError(f"Missing variables for template: {missing}. Expected: {sorted(required)}")


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


