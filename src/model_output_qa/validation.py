"""Validation rules for model output records."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

ALLOWED_LANGUAGES = frozenset({"python", "javascript", "typescript", "sql", "bash", "go", "rust"})
PROMPT_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")
MODEL_NAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,47}$")
FORBIDDEN_ANSWER_PREFIXES = ("TODO", "FIXME", "TBD", "PLACEHOLDER")
BANNED_ANSWER_SUBSTRINGS = (
    "as an ai language model",
    "i cannot assist",
    "i'm unable to",
)
MAX_ANSWER_CHARS = 32_000
MAX_ANSWER_LINES = 500
MAX_BLANK_LINE_RUN = 10
MAX_TAGS = 8
MAX_TAG_LEN = 32
MAX_TOKENS = 128_000


class ModelOutput(BaseModel):
    prompt_id: str
    answer: str = Field(min_length=1, max_length=MAX_ANSWER_CHARS)
    language: str = "python"
    model: str | None = None
    tokens: int | None = Field(default=None, ge=0, le=MAX_TOKENS)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    tags: list[str] | None = None

    @field_validator("language")
    @classmethod
    def language_must_be_allowed(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_LANGUAGES:
            raise ValueError(f"unsupported language: {value}")
        return normalized

    @field_validator("tags")
    @classmethod
    def tags_must_be_bounded(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if len(value) > MAX_TAGS:
            raise ValueError(f"too many tags (max {MAX_TAGS})")
        cleaned: list[str] = []
        for tag in value:
            stripped = tag.strip()
            if not stripped:
                raise ValueError("tags must not be empty strings")
            if len(stripped) > MAX_TAG_LEN:
                raise ValueError(f"tag too long (max {MAX_TAG_LEN} chars)")
            cleaned.append(stripped)
        return cleaned


def _check_prompt_id(prompt_id: str, errors: list[str]) -> None:
    if not PROMPT_ID_RE.match(prompt_id):
        errors.append("prompt_id must start with a letter and use alphanumeric, _, or -")


def _check_model_name(model: str | None, errors: list[str]) -> None:
    if model is None:
        return
    stripped = model.strip()
    if not stripped:
        errors.append("model must not be blank when provided")
        return
    if not MODEL_NAME_RE.match(stripped):
        errors.append("model name must start with alphanumeric and use . _ or -")


def _check_answer_content(answer: str, errors: list[str]) -> None:
    stripped = answer.strip()
    upper = stripped.upper()
    for prefix in FORBIDDEN_ANSWER_PREFIXES:
        if upper.startswith(prefix):
            errors.append(f"placeholder answer ({prefix.lower()})")
            break
    lowered = stripped.lower()
    for phrase in BANNED_ANSWER_SUBSTRINGS:
        if phrase in lowered:
            errors.append(f"banned phrase in answer ({phrase})")
            break
    if len(stripped) < 3:
        errors.append("answer too short (min 3 non-whitespace chars)")
    if stripped.count("\n") > MAX_ANSWER_LINES:
        errors.append(f"answer exceeds line limit ({MAX_ANSWER_LINES})")
    blank_run = 0
    for line in answer.splitlines():
        if not line.strip():
            blank_run += 1
            if blank_run > MAX_BLANK_LINE_RUN:
                errors.append(f"answer exceeds consecutive blank lines ({MAX_BLANK_LINE_RUN})")
                break
        else:
            blank_run = 0


def validate_record(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a single model-output record. Returns (ok, error messages)."""
    errors: list[str] = []
    try:
        ModelOutput.model_validate(data)
    except Exception as exc:
        errors.append(str(exc))
    prompt_id = str(data.get("prompt_id", ""))
    if prompt_id:
        _check_prompt_id(prompt_id, errors)
    answer = str(data.get("answer", ""))
    if answer:
        _check_answer_content(answer, errors)
    _check_model_name(data.get("model"), errors)
    return (len(errors) == 0, errors)


def validate_records(
    records: list[dict[str, Any]],
    *,
    check_duplicate_prompt_ids: bool = False,
) -> list[tuple[int, bool, list[str]]]:
    """Validate many records; returns (index, ok, errors) per row."""
    results: list[tuple[int, bool, list[str]]] = []
    seen_prompt_ids: dict[str, int] = {}
    for index, record in enumerate(records):
        ok, errors = validate_record(record)
        if check_duplicate_prompt_ids:
            prompt_id = str(record.get("prompt_id", ""))
            if prompt_id:
                if prompt_id in seen_prompt_ids:
                    errors = list(errors)
                    errors.append(
                        f"duplicate prompt_id (first seen at index {seen_prompt_ids[prompt_id]})"
                    )
                    ok = False
                else:
                    seen_prompt_ids[prompt_id] = index
        results.append((index, ok, errors))
    return results
