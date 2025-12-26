from pathlib import Path

from model_output_qa.eval.batch import run_batch, write_batch_report, write_batch_report_markdown

FIXTURES = Path(__file__).resolve().parents[1] / "eval" / "fixtures"


def test_run_batch_aggregates(tmp_path):
    report = run_batch(
        [
            FIXTURES / "valid.jsonl",
            FIXTURES / "invalid.jsonl",
        ]
    )
    assert report.total >= 5
    assert report.passed >= 3
    assert report.failed >= 1
    assert len(report.fixtures) == 2
    assert "summary" in report.to_dict()


def test_batch_report_written(tmp_path):
    report = run_batch([FIXTURES / "sample.jsonl"])
    out = tmp_path / "batch.report.json"
    write_batch_report(report, out)
    assert out.exists()
    assert "fixtures" in out.read_text(encoding="utf-8")


def test_batch_markdown_report(tmp_path):
    report = run_batch([FIXTURES / "valid.jsonl", FIXTURES / "unicode.jsonl"])
    out = tmp_path / "batch.report.md"
    write_batch_report_markdown(report, out)
    text = out.read_text(encoding="utf-8")
    assert "# Batch eval report" in text
    assert "Pass rate" in text
