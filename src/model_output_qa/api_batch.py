from fastapi import FastAPI
from pydantic import BaseModel, Field

from model_output_qa.validation import validate_record, validate_records

app = FastAPI(title="model-output-qa", version="0.3.0")


class RecordIn(BaseModel):
    prompt_id: str
    answer: str
    language: str = "python"
    model: str | None = None
    tokens: int | None = Field(default=None, ge=0)


class BatchIn(BaseModel):
    records: list[RecordIn] = Field(min_length=1, max_length=500)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.3.0"}


@app.post("/validate")
def validate(payload: RecordIn):
    ok, errors = validate_record(payload.model_dump())
    return {"valid": ok, "errors": errors}


@app.post("/validate/batch")
def validate_batch(payload: BatchIn):
    rows = validate_records([r.model_dump() for r in payload.records])
    results = [
        {"index": index, "valid": ok, "errors": errors}
        for index, ok, errors in rows
    ]
    passed = sum(1 for row in results if row["valid"])
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "results": results,
    }
