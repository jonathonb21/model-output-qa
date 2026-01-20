# Usage guide

## Install

```bash
pip install -e ".[dev]"
```

## Schema checks

```python
from model_output_qa import check_schema, record_json_schema

schema = record_json_schema()
ok, errors = check_schema({"prompt_id": "demo", "answer": "print('hi')"})
```

## Validate one record (Python)

```python
from model_output_qa import validate_record

ok, errors = validate_record({"prompt_id": "demo", "answer": "print('hi')"})
```

Optional metadata: `model`, `tokens`, `confidence` (0–1), `tags` (max 8).

## HTTP API

```bash
uvicorn model_output_qa.api:app --reload
curl -X POST http://127.0.0.1:8000/validate \
  -H "Content-Type: application/json" \
  -d '{"prompt_id":"demo","answer":"return 1"}'
```

Batch validation (duplicate `prompt_id` values are flagged):

```bash
curl -X POST http://127.0.0.1:8000/validate/batch \
  -H "Content-Type: application/json" \
  -d '{"records":[{"prompt_id":"a","answer":"ok"},{"prompt_id":"b","answer":"TODO"}]}'
```

## Offline eval

Single fixture:

```bash
python -m model_output_qa.eval.run eval/fixtures/sample.jsonl
```

Multiple fixtures (writes `eval/reports/batch.report.json` and `batch.report.md`):

```bash
python -m model_output_qa.eval.run eval/fixtures/valid.jsonl eval/fixtures/invalid.jsonl
```

## Rubric integration (stub)

Start [eval-rubric-api](https://github.com/jonathonb21/eval-rubric-api) and point the client:

```bash
export RUBRIC_API_URL=http://127.0.0.1:8080
```

```python
from model_output_qa import RubricClient

client = RubricClient()
print(client.score("def f(): pass", {"style": "uses a function definition"}))
print(client.score_batch([{"answer": "a"}, {"answer": "b"}], rubric={"style": "clear"}))
```

Or use the API proxy: `POST /score/rubric` with `answer` and `rubric` body fields.

## Validation rules (summary)

| Rule | Detail |
|------|--------|
| `prompt_id` | Letter-first, alphanumeric/`_`/`-`, max 64 chars |
| `language` | Allowlist: python, javascript, typescript, sql, bash, go, rust |
| `answer` | Min 3 chars, no TODO/FIXME prefixes, no banned refusal phrases |
| `model` | Optional; must match name pattern when set |
| `tokens` | Optional; 0–128000 |
| Batch | Optional duplicate `prompt_id` detection |

## Tests

```bash
pytest
```
