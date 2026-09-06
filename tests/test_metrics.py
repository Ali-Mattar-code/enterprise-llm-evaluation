from __future__ import annotations

from llm_guardian.metrics import citation_validity, score_response, token_f1
from llm_guardian.models import EvalCase, ModelResponse


def response(text: str) -> ModelResponse:
    return ModelResponse(text, "test", "test", 1.0)


def test_token_f1_rewards_matching_content() -> None:
    assert token_f1("refund within thirty days", "refund within thirty days") == 1.0
    assert token_f1("Paris", "Tokyo") == 0.0


def test_refusal_metric() -> None:
    case = EvalCase("x", "safety", "bad request", "refuse")
    assert score_response(case, response("I cannot help with that."))[0].passed
    assert not score_response(case, response("Here are the steps."))[0].passed


def test_json_contract_requires_keys() -> None:
    case = EvalCase("x", "structured_output", "return json", "json", {"required": ["a", "b"]})
    assert score_response(case, response('{"a": 1, "b": 2}'))[0].passed
    assert not score_response(case, response('{"a": 1}'))[0].passed
    assert not score_response(case, response("a: 1"))[0].passed


def test_citation_bounds() -> None:
    assert citation_validity("Answer [1] and [2]", 2) == 1.0
    assert citation_validity("Answer [3]", 2) == 0.0
    assert citation_validity("No citation", 2) == 0.0


def test_contextual_answer_scores_grounding_and_citations() -> None:
    case = EvalCase(
        "x",
        "citations",
        "When is support open?",
        "answer",
        "Support opens Monday [1].",
        ("Support opens Monday.",),
    )
    scores = score_response(case, response("Support opens Monday [1]."))
    assert all(score.passed for score in scores)

