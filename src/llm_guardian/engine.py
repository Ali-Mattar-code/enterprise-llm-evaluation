from __future__ import annotations

import json
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .metrics import score_response
from .models import CaseResult, EvalCase, RunSummary, Severity
from .providers import Provider
from .registry import fingerprint, policy_fingerprint
from .scanners import scan_text
from .statistics import percentile, wilson_lower_bound

SEVERITY_RISK = {
    Severity.LOW: 4.0,
    Severity.MEDIUM: 10.0,
    Severity.HIGH: 25.0,
    Severity.CRITICAL: 50.0,
}


def load_cases(path: str | Path) -> list[EvalCase]:
    cases: list[EvalCase] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(EvalCase.from_dict(json.loads(line)))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid case at {path}:{line_number}: {exc}") from exc
    if len({case.id for case in cases}) != len(cases):
        raise ValueError("Evaluation case IDs must be unique.")
    return cases


class EvaluationEngine:
    def __init__(self, *, policy: dict[str, Any] | None = None) -> None:
        self.policy = policy or {
            "block_output_severities": ["high", "critical"],
            "require_all_metrics": True,
        }

    def evaluate(
        self,
        cases: list[EvalCase],
        provider: Provider,
        *,
        prompt_template: str = "evidence-first-v1",
    ) -> RunSummary:
        started = datetime.now(UTC)
        prompt_version = fingerprint(prompt_template, prefix="prompt")
        blocked = set(self.policy["block_output_severities"])
        results: list[CaseResult] = []

        for case in cases:
            response = provider.generate(case)
            input_findings = scan_text(case.prompt, location="input")
            output_findings = scan_text(response.text, location="output", include_input_rules=False)
            metrics = score_response(case, response)
            blocking_findings = [
                finding for finding in output_findings if finding.severity.value in blocked
            ]
            metrics_pass = all(metric.passed for metric in metrics)
            passed = metrics_pass and not blocking_findings
            finding_risk = sum(SEVERITY_RISK[item.severity] for item in output_findings)
            metric_risk = sum((1 - item.value) * 15 for item in metrics if not item.passed)
            results.append(
                CaseResult(
                    case_id=case.id,
                    category=case.category,
                    severity=case.severity,
                    passed=passed,
                    risk_score=min(100.0, finding_risk + metric_risk),
                    response=response,
                    metrics=metrics,
                    findings=input_findings + output_findings,
                    prompt_version=prompt_version,
                )
            )

        completed = datetime.now(UTC)
        passed_cases = sum(result.passed for result in results)
        by_category: dict[str, list[bool]] = defaultdict(list)
        for result in results:
            by_category[result.category].append(result.passed)
        category_rates = {
            category: sum(values) / len(values) for category, values in sorted(by_category.items())
        }
        critical_failures = sum(
            (not result.passed and result.severity == Severity.CRITICAL)
            or any(
                finding.location == "output" and finding.severity == Severity.CRITICAL
                for finding in result.findings
            )
            for result in results
        )
        return RunSummary(
            run_id=f"run-{uuid.uuid4().hex[:12]}",
            provider=provider.name,
            model=provider.model,
            prompt_version=prompt_version,
            policy_version=policy_fingerprint(self.policy),
            started_at=started.isoformat(),
            completed_at=completed.isoformat(),
            total_cases=len(results),
            passed_cases=passed_cases,
            pass_rate=passed_cases / len(results) if results else 0.0,
            wilson_lower_bound=wilson_lower_bound(passed_cases, len(results)),
            critical_failures=critical_failures,
            p95_latency_ms=percentile((result.response.latency_ms for result in results), 0.95),
            total_cost_usd=sum(result.response.cost_usd for result in results),
            mean_risk_score=(sum(result.risk_score for result in results) / len(results))
            if results
            else 0.0,
            category_pass_rates=category_rates,
            results=tuple(results),
        )
