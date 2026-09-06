from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from llm_guardian.cli import app

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_scan_command_reports_and_redacts() -> None:
    result = runner.invoke(app, ["scan", "Contact jordan@example.com", "--redact"])
    assert result.exit_code == 0
    assert "email_address" in result.output
    assert "jordan@example.com" not in result.output.splitlines()[-1]


def test_scan_command_reports_clean_text() -> None:
    result = runner.invoke(app, ["scan", "Summarise the approved policy."])
    assert result.exit_code == 0
    assert "No configured rules matched" in result.output


def test_evaluate_command_writes_run(tmp_path: Path) -> None:
    output = tmp_path / "run.json"
    result = runner.invoke(
        app,
        [
            "evaluate",
            "--dataset",
            str(ROOT / "datasets/evaluation_suite.jsonl"),
            "--output",
            str(output),
        ],
    )
    assert result.exit_code == 0
    assert json.loads(output.read_text())["passed_cases"] == 27


def test_evaluate_rejects_unknown_provider() -> None:
    result = runner.invoke(app, ["evaluate", "--provider", "unknown"])
    assert result.exit_code != 0


def test_gate_command_displays_thresholds(tmp_path: Path) -> None:
    run = tmp_path / "run.json"
    run.write_text(json.dumps({"pass_rate": 0.95, "critical_failures": 0}))
    result = runner.invoke(
        app,
        [
            "gate",
            str(run),
            "--config",
            str(ROOT / "configs/release_gate.yaml"),
        ],
    )
    assert result.exit_code == 0
    assert "pass_rate" in result.output

