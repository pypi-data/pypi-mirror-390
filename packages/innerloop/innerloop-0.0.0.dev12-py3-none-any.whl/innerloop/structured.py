from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

# Preferred: JSON within <json></json> tags (used in XML fallback mode)
JSON_TAG_RE = re.compile(
    r"<json>\s*(.*?)\s*</json>", re.DOTALL | re.IGNORECASE
)

# Legacy: JSON within markdown code fences (backward compatibility)
FENCE_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)
UNLABELED_FENCE_RE = re.compile(r"```\s*(.*?)\s*```", re.DOTALL)


def build_structured_prompt(
    prompt: str,
    model_cls: type[T],
    *,
    instructions: str | None = None,
    output_file: str | None = None,
) -> str:
    """Decorate a user prompt with explicit JSON schema instructions.

    Supports dual-mode structured outputs:
    - File mode: LLM writes JSON directly to output_file (when provided)
    - XML fallback: LLM returns JSON in <json></json> tags (when output_file=None)

    Args:
        prompt: The base user prompt
        model_cls: Pydantic model defining the expected output structure
        instructions: Custom schema instructions (overrides default behavior)
        output_file: Path where JSON should be written. If None, uses XML fallback mode.

    Returns:
        Decorated prompt with schema and output instructions
    """
    schema = json.dumps(model_cls.model_json_schema(), indent=2)

    if instructions is None:
        if output_file:
            # File mode: LLM writes to file with XML fallback
            instructions = (
                f"Write a valid JSON object matching the schema to: {output_file}\n"
                f"The parent directory will exist. Use file operations or bash redirection.\n"
                f"If you cannot write files, return the JSON in <json></json> tags as fallback."
            )
        else:
            # XML fallback mode only
            instructions = (
                "Return a valid JSON object matching the schema within <json></json> tags.\n"
                "Do not include any explanations outside the tags."
            )

    return (
        f"{prompt}\n\n"
        f"{instructions}\n"
        f"Schema:\n"
        f"<schema>\n"
        f"{schema}\n"
        f"</schema>"
    )


def build_structured_reprompt(base_prompt: str, validation_error: str) -> str:
    """Build a retry prompt for structured output that failed validation.

    This is the same retry strategy used internally by async_invoke_structured.
    Use this when you need to request a corrected response after validation fails.

    Args:
        base_prompt: The original prompt from build_structured_prompt()
                     (includes user prompt + schema)
        validation_error: The validation error message, typically str(ValidationError)

    Returns:
        A new prompt that preserves the original schema and adds error context

    Example:
        >>> from pydantic import BaseModel, ValidationError
        >>> class User(BaseModel):
        ...     name: str
        ...     age: int
        >>> prompt = build_structured_prompt("Extract: John, thirty", User)
        >>> # ... send prompt, get invalid JSON back ...
        >>> try:
        ...     User.model_validate_json('{"name": "John", "age": "thirty"}')
        ... except ValidationError as e:
        ...     retry = build_structured_reprompt(prompt, str(e))
        ...     # ... send retry prompt for correction ...
    """
    return (
        f"{base_prompt}\n\n"
        "Your previous JSON failed validation.\n"
        f"Error: {validation_error}\n"
        "Please return ONLY a corrected JSON object that satisfies the schema."
    )


def _find_balanced_json(text: str) -> str | None:
    """Find the first balanced JSON object/array outside code fences.

    Handles strings and escapes to avoid counting braces within quotes.
    Returns the JSON substring or None.
    """
    in_string = False
    escape = False
    stack: list[str] = []
    start = -1
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
            if ch in "[{":
                if start == -1:
                    start = i
                stack.append(ch)
            elif ch in "]}":
                if not stack:
                    continue
                top = stack.pop()
                if (top == "[" and ch != "]") or (top == "{" and ch != "}"):
                    # mismatch; reset
                    stack.clear()
                    start = -1
                elif not stack and start != -1:
                    return text[start : i + 1]
    return None


def _extract_json_snippet(text: str) -> str:
    """Return the best-effort JSON snippet from the text or raise.

    Order of preference:
    1) <json></json> tags (primary for XML fallback mode)
    2) labeled ```json fence (backward compatibility)
    3) unlabeled fence that looks like JSON
    4) first balanced JSON object/array in free text
    """
    # Try <json> tags first (preferred for fallback mode)
    m = JSON_TAG_RE.search(text)
    if m:
        return m.group(1).strip()

    # Try labeled JSON fence
    m = FENCE_RE.search(text)
    if m:
        return m.group(1).strip()

    # Try unlabeled fence
    unlabeled = UNLABELED_FENCE_RE.search(text)
    if unlabeled:
        content = unlabeled.group(1).strip()
        if content.startswith(("{", "[")):
            return content

    # Last resort: balanced JSON in free text
    snippet = _find_balanced_json(text)
    if snippet is None:
        raise ValueError("No JSON block found in the response.")
    return snippet


def _extract_and_parse_json(text: str, model_cls: type[T]) -> T:
    """Extract the best JSON snippet then validate against the model."""
    snippet = _extract_json_snippet(text)
    try:
        return model_cls.model_validate_json(snippet)
    except ValidationError as e:
        raise ValueError(
            f"Failed to validate extracted JSON against {model_cls.__name__}."
        ) from e


def create_structured_parser(model_cls: type[T]) -> Callable[[str], T]:
    """Factory returning a parser that extracts and validates a JSON code block."""

    def parser(raw_text: str) -> T:
        return _extract_and_parse_json(raw_text, model_cls)

    return parser
