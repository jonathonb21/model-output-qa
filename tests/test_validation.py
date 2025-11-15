import pytest

from model_output_qa.validation import validate_record, validate_records


def test_valid_record():
    ok, errors = validate_record({"prompt_id": "p1", "answer": "print(1)"})
    assert ok and not errors


def test_rejects_placeholder():
    ok, errors = validate_record({"prompt_id": "p2", "answer": "TODO fix"})
    assert not ok
    assert any("placeholder" in e.lower() for e in errors)


def test_rejects_invalid_prompt_id():
    ok, errors = validate_record({"prompt_id": "9bad", "answer": "print(1)"})
    assert not ok


def test_rejects_unsupported_language():
    ok, errors = validate_record({"prompt_id": "p3", "answer": "print(1)", "language": "cobol"})
    assert not ok


def test_accepts_optional_model_and_tokens():
    ok, errors = validate_record(
        {
            "prompt_id": "p4",
            "answer": "select 1",
            "language": "sql",
            "model": "gpt-demo",
            "tokens": 10,
        }
    )
    assert ok and not errors


def test_validate_records_batch():
    rows = validate_records(
        [
            {"prompt_id": "a", "answer": "ok()"},
            {"prompt_id": "b", "answer": "FIXME"},
        ]
    )
    assert rows[0][1] is True
    assert rows[1][1] is False


def test_rejects_answer_too_short():
    ok, _ = validate_record({"prompt_id": "x1", "answer": "  "})
    assert not ok


def test_rejects_banned_phrase():
    ok, errors = validate_record(
        {
            "prompt_id": "refusal",
            "answer": "As an AI language model I cannot help.",
        }
    )
    assert not ok
    assert any("banned phrase" in e for e in errors)


def test_rejects_blank_model_name():
    ok, errors = validate_record({"prompt_id": "m1", "answer": "print(1)", "model": "  "})
    assert not ok
    assert any("model" in e for e in errors)


def test_accepts_tags_and_confidence():
    ok, errors = validate_record(
        {
            "prompt_id": "meta",
            "answer": "return 42",
            "tags": ["math"],
            "confidence": 0.75,
        }
    )
    assert ok and not errors


def test_rejects_too_many_tags():
    ok, _ = validate_record(
        {
            "prompt_id": "tags",
            "answer": "return 1",
            "tags": [f"t{i}" for i in range(9)],
        }
    )
    assert not ok


def test_duplicate_prompt_ids_in_batch():
    rows = validate_records(
        [
            {"prompt_id": "dup", "answer": "one"},
            {"prompt_id": "dup", "answer": "two"},
        ],
        check_duplicate_prompt_ids=True,
    )
    assert rows[0][1] is True
    assert rows[1][1] is False
    assert any("duplicate" in e for e in rows[1][2])
