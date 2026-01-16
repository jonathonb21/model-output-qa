# Eval fixtures

| File | Purpose |
|------|---------|
| `sample.jsonl` | Minimal smoke set (1 pass, 1 fail) |
| `valid.jsonl` | Records that should pass all rules |
| `invalid.jsonl` | Schema, language, placeholder, and id failures |
| `mixed_batch.jsonl` | Used by batch eval CLI demos |
| `edge_cases.jsonl` | Tags, model blank, banned phrases |
| `unicode.jsonl` | Non-ASCII content in answers |

Run:

```bash
python -m model_output_qa.eval.run eval/fixtures/sample.jsonl
python -m model_output_qa.eval.run eval/fixtures/*.jsonl
```

Multi-fixture batch writes `eval/reports/batch.report.json` and `batch.report.md`.
