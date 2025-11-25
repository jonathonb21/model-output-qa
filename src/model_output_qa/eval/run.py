"""Offline eval over a single JSONL fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from model_output_qa.eval.batch import (
    eval_fixture,
    run_batch,
    write_batch_report,
    write_batch_report_markdown,
)
from model_output_qa.validation import validate_record


def eval_file(path: Path, *, max_failures: int = 50) -> dict[str, object]:
    result = eval_fixture(path, max_failures=max_failures)
    return {
        "path": result.path,
        "total": result.total,
        "passed": result.passed,
        "failed": result.failed,
        "pass_rate": result.pass_rate,
        "failures": result.failures,
    }


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(
            "usage: python -m model_output_qa.eval.run <file.jsonl> [more.jsonl ...]",
            file=sys.stderr,
        )
        raise SystemExit(2)

    paths = [Path(a) for a in args]
    if len(paths) == 1:
        report = eval_file(paths[0])
        out = paths[0].with_suffix(".report.json")
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(
            json.dumps(
                {"total": report["total"], "passed": report["passed"], "failed": report["failed"]}
            )
        )
        return

    batch = run_batch(paths)
    report_dir = Path("eval/reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    write_batch_report(batch, report_dir / "batch.report.json")
    write_batch_report_markdown(batch, report_dir / "batch.report.md")
    print(json.dumps({"total": batch.total, "passed": batch.passed, "failed": batch.failed}))


if __name__ == "__main__":
    main()
