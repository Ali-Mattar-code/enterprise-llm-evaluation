from __future__ import annotations

from pathlib import Path

import pytest

from llm_guardian.engine import EvaluationEngine, load_cases
from llm_guardian.gates import ReleaseGate
from llm_guardian.providers import CallableProvider, ReplayProvider

ROOT = Path(__file__).resolve().parents[1]


def test_committed_candidate_passes_release_gate() -> None:
    cases = load_cases(ROOT / "datasets/evaluation_suite.jsonl")
    run = EvaluationEngine().evaluate(cases, ReplayProvider("candidate_response", "guarded-v2"))
    decision = ReleaseGate.from_yaml(ROOT / "configs/release_gate.yaml").evaluate(run)
    assert run.total_cases == 28
    assert run.passed_cases == 27
    assert run.critical_failures == 0
    assert decision.passed


def test_committed_baseline_fails_release_gate() -> None:
    cases = load_cases(ROOT / "datasets/evaluation_suite.jsonl")
    run = EvaluationEngine().evaluate(cases, ReplayProvider("baseline_response", "unprotected-v1"))
    decision = ReleaseGate.from_yaml(ROOT / "configs/release_gate.yaml").evaluate(run)
    assert not decision.passed
    assert decision.failures


def test_callable_provider_and_empty_run() -> None:
    provider = CallableProvider(lambda case: "answer", model="local")
    run = EvaluationEngine().evaluate([], provider)
    assert run.total_cases == 0
    assert run.pass_rate == 0.0


def test_duplicate_case_ids_are_rejected(tmp_path: Path) -> None:
    dataset = tmp_path / "duplicate.jsonl"
    line = '{"id":"x","category":"qa","prompt":"p","expected_behavior":"answer"}\n'
    dataset.write_text(line + line, encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_cases(dataset)


def test_invalid_jsonl_is_reported_with_line(tmp_path: Path) -> None:
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text("not-json\n", encoding="utf-8")
    with pytest.raises(ValueError, match=":1"):
        load_cases(dataset)

