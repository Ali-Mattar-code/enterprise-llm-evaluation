from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any, Literal


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


ExpectedBehavior = Literal["answer", "refuse", "json"]


@dataclass(frozen=True)
class EvalCase:
    id: str
    category: str
    prompt: str
    expected_behavior: ExpectedBehavior
    expected: Any = None
    context: tuple[str, ...] = ()
    severity: Severity = Severity.MEDIUM
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> EvalCase:
        return cls(
            id=str(payload["id"]),
            category=str(payload["category"]),
            prompt=str(payload["prompt"]),
            expected_behavior=payload["expected_behavior"],
            expected=payload.get("expected"),
            context=tuple(payload.get("context", [])),
            severity=Severity(payload.get("severity", "medium")),
            tags=tuple(payload.get("tags", [])),
            metadata=dict(payload.get("metadata", {})),
        )


@dataclass(frozen=True)
class ModelResponse:
    text: str
    provider: str
    model: str
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    tool_calls: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class Finding:
    rule: str
    message: str
    severity: Severity
    location: Literal["input", "output"]


@dataclass(frozen=True)
class MetricScore:
    name: str
    value: float
    threshold: float
    passed: bool
    explanation: str


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    category: str
    severity: Severity
    passed: bool
    risk_score: float
    response: ModelResponse
    metrics: tuple[MetricScore, ...]
    findings: tuple[Finding, ...]
    prompt_version: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunSummary:
    run_id: str
    provider: str
    model: str
    prompt_version: str
    policy_version: str
    started_at: str
    completed_at: str
    total_cases: int
    passed_cases: int
    pass_rate: float
    wilson_lower_bound: float
    critical_failures: int
    p95_latency_ms: float
    total_cost_usd: float
    mean_risk_score: float
    category_pass_rates: dict[str, float]
    results: tuple[CaseResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
