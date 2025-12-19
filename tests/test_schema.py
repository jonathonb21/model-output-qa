from model_output_qa.schema import (
    check_required_fields,
    check_schema,
    check_unknown_fields,
    record_json_schema,
)


def test_record_json_schema_has_required_properties():
    schema = record_json_schema()
    assert "properties" in schema
    assert "prompt_id" in schema["properties"]
    assert "answer" in schema["properties"]


def test_check_required_fields_detects_missing():
    assert check_required_fields({"prompt_id": "p1"}) == ["answer"]
    assert check_required_fields({"answer": "ok"}) == ["prompt_id"]


def test_check_unknown_fields():
    unknown = check_unknown_fields({"prompt_id": "p1", "answer": "ok", "extra": 1})
    assert unknown == ["extra"]


def test_check_schema_rejects_unknown_and_missing():
    ok, errors = check_schema({"prompt_id": "p1"})
    assert not ok
    assert any("missing required field" in e for e in errors)

    ok, errors = check_schema({"prompt_id": "p1", "answer": "ok", "bogus": True})
    assert not ok
    assert any("unknown fields" in e for e in errors)


def test_check_schema_accepts_minimal_record():
    ok, errors = check_schema({"prompt_id": "p1", "answer": "return 1"})
    assert ok and not errors
