# Architecture

## Components

| Module | Role |
|--------|------|
| `schema.py` | JSON Schema export and required/unknown field checks |
| `validation.py` | Pydantic schema + rule checks for model output JSON |
| `api.py` | FastAPI HTTP surface (`/validate`, `/validate/batch`, `/score/rubric`) |
| `eval/run.py` | CLI for single- or multi-fixture offline eval |
| `eval/batch.py` | Aggregated batch reports with JSON and Markdown export |
| `rubric/client.py` | Optional HTTP client to `eval-rubric-api` |

## Data flow

1. Producers emit JSONL lines (`prompt_id`, `answer`, `language`, optional metadata).
2. `validate_record` returns structured errors without persisting state.
3. Batch eval writes `*.report.json`, `eval/reports/batch.report.json`, and optional Markdown.
4. When a rubric service is available, `RubricClient.score` / `score_batch` posts answers for dimension scores.

## Non-goals

- No database or queue (stateless validation only).
- No embedded LLM judge — rubric scoring is delegated to `eval-rubric-api`.
- No authentication on the demo API (add reverse proxy in production).
