# model-output-qa

Validate model-generated JSON outputs for technical QA workflows.

```bash
pip install -e ".[dev]"
uvicorn model_output_qa.api:app --reload
pytest
```
