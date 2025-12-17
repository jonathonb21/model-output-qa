"""JSON schema helpers for model output records."""

from __future__ import annotations

from typing import Any

from model_output_qa.validation import ALLOWED_LANGUAGES, ModelOutput

REQUIRED_FIELDS = frozenset({"prompt_id", "answer"})


def record_json_schema() -> dict[str, Any]:
    """Return JSON Schema for a model output record."""
    return ModelOutput.model_json_schema()


def check_required_fields(data: dict[str, Any]) -> list[str]:
    """Return missing required field names."""
    missing: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] in (None, ""):
            missing.append(field)
    return missing


def check_unknown_fields(data: dict[str, Any]) -> list[str]:
    """Return keys not declared on ModelOutput."""
    allowed = set(ModelOutput.model_fields.keys())
    return sorted(k for k in data if k not in allowed)


def check_schema(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Lightweight schema checks before full rule validation."""
    errors: list[str] = []
    for field in check_required_fields(data):
        errors.append(f"missing required field: {field}")
    unknown = check_unknown_fields(data)
    if unknown:
        errors.append(f"unknown fields: {', '.join(unknown)}")
    language = data.get("language")
    if language is not None and str(language).strip().lower() not in ALLOWED_LANGUAGES:
        errors.append(f"unsupported language in schema check: {language}")
    return (len(errors) == 0, errors)
