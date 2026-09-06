from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def fingerprint(payload: Any, *, prefix: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def dataset_fingerprint(path: str | Path) -> str:
    content = Path(path).read_bytes()
    return f"dataset-{hashlib.sha256(content).hexdigest()[:12]}"


def policy_fingerprint(policy: dict[str, Any]) -> str:
    return fingerprint(policy, prefix="policy")

