# Changelog

## 0.4.0 — 2026-03-28

- `schema.py`: JSON Schema export and lightweight required/unknown field checks.
- Validation: banned answer phrases, model name pattern, tags/confidence fields, blank-line limits, duplicate `prompt_id` detection in batch mode.
- Batch reports: summary block, optional Markdown export (`batch.report.md`).
- Rubric stub: `score_batch` for multi-record best-effort scoring.
- Fixtures: `edge_cases.jsonl`, `unicode.jsonl`.
- Docs and CI refreshed for the 0.4.0 release.

## 0.3.0 — 2026-03-18

- Expanded validation: language allowlist, prompt_id pattern, placeholder prefixes, line limits.
- Batch eval reports across multiple JSONL fixtures (`eval/batch.py`, multi-file CLI).
- `RubricClient` stub for optional `eval-rubric-api` scoring via `RUBRIC_API_URL`.
- FastAPI `/validate/batch` and `/score/rubric` endpoints.
- Additional fixtures (`valid`, `invalid`, `mixed_batch`) and docs (`docs/ARCHITECTURE.md`, `docs/USAGE.md`).
- GitHub Actions CI on Python 3.11 and 3.12.

## 0.2.0 — 2026-01-12

- Per-record failure details in single-fixture eval reports.
- Optional `model` and `tokens` fields on records.

## 0.1.0 — 2025-11-01

- Initial FastAPI `/validate` service and offline JSONL eval CLI.
