from __future__ import annotations

import math
from collections.abc import Iterable


def wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    """Return the lower Wilson confidence bound for a binomial success rate."""
    if total <= 0:
        return 0.0
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = proportion + z**2 / (2 * total)
    margin = z * math.sqrt((proportion * (1 - proportion) + z**2 / (4 * total)) / total)
    return max(0.0, (centre - margin) / denominator)


def percentile(values: Iterable[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)


def jensen_shannon_divergence(left: dict[str, float], right: dict[str, float]) -> float:
    """Bounded distribution drift in bits; missing categories are treated as zero."""
    keys = set(left) | set(right)
    if not keys:
        return 0.0
    left_total = sum(max(left.get(key, 0.0), 0.0) for key in keys) or 1.0
    right_total = sum(max(right.get(key, 0.0), 0.0) for key in keys) or 1.0
    p = {key: max(left.get(key, 0.0), 0.0) / left_total for key in keys}
    q = {key: max(right.get(key, 0.0), 0.0) / right_total for key in keys}
    m = {key: (p[key] + q[key]) / 2 for key in keys}

    def kl(a: dict[str, float], b: dict[str, float]) -> float:
        return sum(a[key] * math.log2(a[key] / b[key]) for key in keys if a[key] > 0)

    return (kl(p, m) + kl(q, m)) / 2

