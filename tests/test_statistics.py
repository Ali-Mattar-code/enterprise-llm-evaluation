from __future__ import annotations

import pytest

from llm_guardian.statistics import jensen_shannon_divergence, percentile, wilson_lower_bound


def test_wilson_bound_is_conservative() -> None:
    assert wilson_lower_bound(27, 28) < 27 / 28
    assert wilson_lower_bound(27, 28) == pytest.approx(0.822874, rel=1e-5)


def test_wilson_empty_sample() -> None:
    assert wilson_lower_bound(0, 0) == 0.0


def test_percentile_interpolates_and_handles_empty() -> None:
    assert percentile([1.0, 2.0, 3.0], 0.5) == 2.0
    assert percentile([], 0.95) == 0.0


def test_jensen_shannon_is_bounded_and_symmetric() -> None:
    left = {"safe": 0.9, "unsafe": 0.1}
    right = {"safe": 0.1, "unsafe": 0.9}
    assert jensen_shannon_divergence(left, right) == jensen_shannon_divergence(right, left)
    assert 0 < jensen_shannon_divergence(left, right) <= 1
    assert jensen_shannon_divergence({}, {}) == 0

