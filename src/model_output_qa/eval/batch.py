"""Batch offline eval over multiple JSONL fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from model_output_qa.validation import validate_record


@dataclass
class FixtureResult:
    path: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    failures: list[dict[str, object]] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.passed / self.total, 4)


@dataclass
class BatchReport:
    fixtures: list[FixtureResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(f.total for f in self.fixtures)

    @property
    def passed(self) -> int:
        return sum(f.passed for f in self.fixtures)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return round(self.passed / self.total, 4)

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": {
                "fixtures": len(self.fixtures),
                "total": self.total,
                "passed": self.passed,
                "failed": self.failed,
                "pass_rate": self.pass_rate,
            },
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "fixtures": [
                {
                    "path": f.path,
                    "total": f.total,
                    "passed": f.passed,
                    "failed": f.failed,
                    "pass_rate": f.pass_rate,
                    "failures": f.failures,
                }
                for f in self.fixtures
            ],
        }


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            records.append({"_parse_error": str(exc), "_line": line_no})
    return records


def eval_fixture(path: Path, *, max_failures: int = 20) -> FixtureResult:
    result = FixtureResult(path=str(path))
    for index, record in enumerate(_load_jsonl(path)):
        if "_parse_error" in record:
            result.total += 1
            result.failed += 1
            if len(result.failures) < max_failures:
                result.failures.append(
                    {"index": index, "errors": [f"json parse: {record['_parse_error']}"]}
                )
            continue
        result.total += 1
        ok, errors = validate_record(record)
        if ok:
            result.passed += 1
        else:
            result.failed += 1
            if len(result.failures) < max_failures:
                result.failures.append(
                    {
                        "index": index,
                        "prompt_id": record.get("prompt_id"),
                        "errors": errors,
                    }
                )
    return result


def run_batch(paths: list[Path], *, max_failures: int = 20) -> BatchReport:
    report = BatchReport()
    for path in paths:
        report.fixtures.append(eval_fixture(path, max_failures=max_failures))
    return report


def write_batch_report(report: BatchReport, out_path: Path) -> None:
    out_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")


def write_batch_report_markdown(report: BatchReport, out_path: Path) -> None:
    lines = [
        "# Batch eval report",
        "",
        f"- Fixtures: {len(report.fixtures)}",
        f"- Total records: {report.total}",
        f"- Passed: {report.passed}",
        f"- Failed: {report.failed}",
        f"- Pass rate: {report.pass_rate:.2%}",
        "",
        "## Per fixture",
        "",
    ]
    for fixture in report.fixtures:
        lines.append(f"### `{fixture.path}`")
        lines.append("")
        lines.append(
            f"- {fixture.passed}/{fixture.total} passed ({fixture.pass_rate:.2%})"
        )
        if fixture.failures:
            lines.append(f"- Sample failures: {len(fixture.failures)}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
