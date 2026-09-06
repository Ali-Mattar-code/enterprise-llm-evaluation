from __future__ import annotations

from pathlib import Path

import pytest

from llm_guardian.storage import ReviewQueue


def test_review_queue_is_idempotent_and_resolvable(tmp_path: Path) -> None:
    queue = ReviewQueue(tmp_path / "reviews.sqlite")
    first = queue.enqueue("run-1", "case-1", 50.0, {"reason": "unsafe"})
    replay = queue.enqueue("run-1", "case-1", 50.0, {"reason": "unsafe"})
    assert first == replay
    assert len(queue.pending()) == 1
    queue.decide(first, reviewer="reviewer@example.com", decision="reject")
    assert queue.pending() == []


def test_review_queue_validates_decisions(tmp_path: Path) -> None:
    queue = ReviewQueue(tmp_path / "reviews.sqlite")
    item = queue.enqueue("run-1", "case-1", 25.0, {})
    with pytest.raises(ValueError, match="approve or reject"):
        queue.decide(item, reviewer="Ali", decision="maybe")
    with pytest.raises(KeyError, match="not found"):
        queue.decide(999, reviewer="Ali", decision="approve")

