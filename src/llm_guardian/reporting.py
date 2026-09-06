from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .gates import GateDecision
from .models import RunSummary
from .statistics import jensen_shannon_divergence


def comparison_payload(
    baseline: RunSummary, candidate: RunSummary, decision: GateDecision
) -> dict[str, object]:
    return {
        "evidence_level": "deterministic-replay-benchmark",
        "interpretation": (
            "Measures evaluator and policy behavior on committed fixtures; it is not a claim about "
            "any external foundation model."
        ),
        "baseline": _compact(baseline),
        "candidate": _compact(candidate),
        "change": {
            "pass_rate_points": candidate.pass_rate - baseline.pass_rate,
            "critical_failures": candidate.critical_failures - baseline.critical_failures,
            "mean_risk_score": candidate.mean_risk_score - baseline.mean_risk_score,
            "category_distribution_jsd": jensen_shannon_divergence(
                baseline.category_pass_rates, candidate.category_pass_rates
            ),
        },
        "release_gate": {
            "passed": decision.passed,
            "checks": [asdict(check) for check in decision.checks],
        },
    }


def _compact(run: RunSummary) -> dict[str, object]:
    return {
        "model": run.model,
        "total_cases": run.total_cases,
        "passed_cases": run.passed_cases,
        "pass_rate": run.pass_rate,
        "wilson_lower_bound": run.wilson_lower_bound,
        "critical_failures": run.critical_failures,
        "p95_latency_ms": run.p95_latency_ms,
        "total_cost_usd": run.total_cost_usd,
        "mean_risk_score": run.mean_risk_score,
        "category_pass_rates": run.category_pass_rates,
    }


def write_json(path: str | Path, payload: object) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_markdown_report(path: str | Path, payload: dict[str, object]) -> None:
    baseline = payload["baseline"]
    candidate = payload["candidate"]
    gate = payload["release_gate"]
    assert isinstance(baseline, dict) and isinstance(candidate, dict) and isinstance(gate, dict)
    status = "PASS" if gate["passed"] else "FAIL"
    lines = [
        "# Evaluation report",
        "",
        f"**Release decision: {status}**",
        "",
        "> Evidence level: deterministic replay benchmark. These results validate the committed",
        "> evaluation and guardrail control plane; they are not external-model performance claims.",
        "",
        "| Measure | Baseline | Candidate |",
        "|---|---:|---:|",
        f"| Passed cases | {baseline['passed_cases']}/{baseline['total_cases']} | "
        f"{candidate['passed_cases']}/{candidate['total_cases']} |",
        f"| Pass rate | {baseline['pass_rate']:.1%} | {candidate['pass_rate']:.1%} |",
        f"| Wilson lower bound | {baseline['wilson_lower_bound']:.1%} | "
        f"{candidate['wilson_lower_bound']:.1%} |",
        f"| Critical failures | {baseline['critical_failures']} | "
        f"{candidate['critical_failures']} |",
        f"| Mean risk score | {baseline['mean_risk_score']:.2f} | "
        f"{candidate['mean_risk_score']:.2f} |",
        "",
        "## Candidate category results",
        "",
        "| Category | Pass rate |",
        "|---|---:|",
    ]
    for category, rate in candidate["category_pass_rates"].items():
        lines.append(f"| {category.replace('_', ' ').title()} | {rate:.1%} |")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")

