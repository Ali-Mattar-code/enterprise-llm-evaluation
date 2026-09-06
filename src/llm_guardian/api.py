from __future__ import annotations

import os
from typing import Any

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install llm-guardian[api] to run the service.") from exc

from .engine import EvaluationEngine
from .models import EvalCase
from .providers import ReplayProvider
from .scanners import redact_sensitive, scan_text
from .storage import ReviewQueue

app = FastAPI(
    title="LLM Guardian",
    version="0.1.0",
    description="Evaluation, red-team scanning, and human approval controls for LLM releases.",
)
review_queue = ReviewQueue(os.getenv("LLM_GUARDIAN_REVIEW_DB", "artifacts/local/reviews.sqlite"))


class ScanRequest(BaseModel):
    text: str = Field(min_length=1, max_length=50_000)
    redact: bool = True


class CaseRequest(BaseModel):
    case: dict[str, Any]
    response_key: str = "candidate_response"
    model: str = "guarded-v2"


class DecisionRequest(BaseModel):
    reviewer: str = Field(min_length=2, max_length=100)
    decision: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "llm-guardian"}


@app.post("/scan")
def scan(request: ScanRequest) -> dict[str, Any]:
    findings = scan_text(request.text, location="input")
    return {
        "findings": [finding.__dict__ for finding in findings],
        "redacted_text": redact_sensitive(request.text) if request.redact else None,
    }


@app.post("/evaluate")
def evaluate(request: CaseRequest) -> dict[str, Any]:
    try:
        case = EvalCase.from_dict(request.case)
        summary = EvaluationEngine().evaluate(
            [case], ReplayProvider(request.response_key, model=request.model)
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    result = summary.results[0]
    if not result.passed or result.risk_score >= 20:
        review_queue.enqueue(summary.run_id, result.case_id, result.risk_score, result.to_dict())
    return summary.to_dict()


@app.get("/reviews")
def reviews() -> list[dict[str, Any]]:
    return [review_queue.serialize(item) for item in review_queue.pending()]


@app.post("/reviews/{item_id}/decision")
def decide(item_id: int, request: DecisionRequest) -> dict[str, str]:
    try:
        review_queue.decide(item_id, reviewer=request.reviewer, decision=request.decision)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "resolved"}
