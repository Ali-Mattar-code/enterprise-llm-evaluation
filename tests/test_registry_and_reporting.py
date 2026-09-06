from __future__ import annotations

import json
from pathlib import Path

from llm_guardian.engine import EvaluationEngine, load_cases
from llm_guardian.gates import ReleaseGate
from llm_guardian.providers import ReplayProvider
from llm_guardian.registry import dataset_fingerprint, fingerprint
from llm_guardian.reporting import comparison_payload, write_json, write_markdown_report

ROOT = Path(__file__).resolve().parents[1]


def test_fingerprints_are_stable(tmp_path: Path) -> None:
    assert fingerprint({"b": 2, "a": 1}, prefix="x") == fingerprint(
        {"a": 1, "b": 2}, prefix="x"
    )
    path = tmp_path / "data"
    path.write_text("stable", encoding="utf-8")
    assert dataset_fingerprint(path).startswith("dataset-")


def test_reports_are_machine_and_human_readable(tmp_path: Path) -> None:
    cases = load_cases(ROOT / "datasets/evaluation_suite.jsonl")
    engine = EvaluationEngine()
    baseline = engine.evaluate(cases, ReplayProvider("baseline_response", "baseline"))
    candidate = engine.evaluate(cases, ReplayProvider("candidate_response", "candidate"))
    decision = ReleaseGate.from_yaml(ROOT / "configs/release_gate.yaml").evaluate(candidate)
    payload = comparison_payload(baseline, candidate, decision)
    json_path = tmp_path / "comparison.json"
    md_path = tmp_path / "report.md"
    write_json(json_path, payload)
    write_markdown_report(md_path, payload)
    assert json.loads(json_path.read_text())["release_gate"]["passed"] is True
    assert "Release decision: PASS" in md_path.read_text()

