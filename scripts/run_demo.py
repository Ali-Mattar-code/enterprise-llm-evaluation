from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llm_guardian.engine import EvaluationEngine, load_cases  # noqa: E402
from llm_guardian.gates import ReleaseGate  # noqa: E402
from llm_guardian.providers import ReplayProvider  # noqa: E402
from llm_guardian.reporting import (  # noqa: E402
    comparison_payload,
    write_json,
    write_markdown_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the deterministic release-gate demonstration."
    )
    parser.add_argument(
        "--check-clean",
        action="store_true",
        help="Evaluate the candidate without rewriting committed artifacts (used by CI).",
    )
    args = parser.parse_args()

    cases = load_cases(ROOT / "datasets/evaluation_suite.jsonl")
    engine = EvaluationEngine()
    baseline = engine.evaluate(
        cases,
        ReplayProvider("baseline_response", model="unprotected-v1"),
    )
    candidate = engine.evaluate(
        cases,
        ReplayProvider("candidate_response", model="guarded-v2"),
    )
    gate = ReleaseGate.from_yaml(ROOT / "configs/release_gate.yaml")
    decision = gate.evaluate(candidate)
    payload = comparison_payload(baseline, candidate, decision)

    if not args.check_clean:
        output = ROOT / "artifacts/demo"
        write_json(output / "comparison.json", payload)
        write_markdown_report(output / "report.md", payload)

    print(
        f"baseline={baseline.pass_rate:.1%} candidate={candidate.pass_rate:.1%} "
        f"critical_failures={candidate.critical_failures} "
        f"gate={'PASS' if decision.passed else 'FAIL'}"
    )
    return 0 if decision.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
