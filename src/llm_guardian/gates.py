from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .models import RunSummary


@dataclass(frozen=True)
class GateCheck:
    name: str
    actual: float
    threshold: float
    operator: str
    passed: bool


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    checks: tuple[GateCheck, ...]

    @property
    def failures(self) -> tuple[GateCheck, ...]:
        return tuple(check for check in self.checks if not check.passed)


class ReleaseGate:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config

    @classmethod
    def from_yaml(cls, path: str | Path) -> ReleaseGate:
        return cls(yaml.safe_load(Path(path).read_text(encoding="utf-8")))

    def evaluate(self, run: RunSummary) -> GateDecision:
        thresholds = self.config["thresholds"]
        checks = [
            self._minimum("pass_rate", run.pass_rate, thresholds["min_pass_rate"]),
            self._minimum(
                "wilson_lower_bound",
                run.wilson_lower_bound,
                thresholds["min_wilson_lower_bound"],
            ),
            self._maximum(
                "critical_failures",
                float(run.critical_failures),
                float(thresholds["max_critical_failures"]),
            ),
            self._maximum(
                "p95_latency_ms", run.p95_latency_ms, thresholds["max_p95_latency_ms"]
            ),
            self._maximum(
                "total_cost_usd", run.total_cost_usd, thresholds["max_total_cost_usd"]
            ),
            self._maximum(
                "mean_risk_score", run.mean_risk_score, thresholds["max_risk_score"]
            ),
        ]
        for category, minimum in self.config.get("category_minimums", {}).items():
            checks.append(
                self._minimum(
                    f"category:{category}", run.category_pass_rates.get(category, 0.0), minimum
                )
            )
        return GateDecision(passed=all(check.passed for check in checks), checks=tuple(checks))

    @staticmethod
    def _minimum(name: str, actual: float, threshold: float) -> GateCheck:
        return GateCheck(name, actual, threshold, ">=", actual >= threshold)

    @staticmethod
    def _maximum(name: str, actual: float, threshold: float) -> GateCheck:
        return GateCheck(name, actual, threshold, "<=", actual <= threshold)

