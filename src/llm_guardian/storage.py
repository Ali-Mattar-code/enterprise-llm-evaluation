from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ReviewItem:
    id: int
    run_id: str
    case_id: str
    risk_score: float
    payload: dict[str, Any]
    status: str
    reviewer: str | None
    decision: str | None
    created_at: str


class ReviewQueue:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    case_id TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    reviewer TEXT,
                    decision TEXT,
                    created_at TEXT NOT NULL,
                    UNIQUE(run_id, case_id)
                )
                """
            )

    def enqueue(self, run_id: str, case_id: str, risk_score: float, payload: dict[str, Any]) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """INSERT OR IGNORE INTO reviews
                (run_id, case_id, risk_score, payload, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (run_id, case_id, risk_score, json.dumps(payload), datetime.now(UTC).isoformat()),
            )
            if cursor.lastrowid:
                return int(cursor.lastrowid)
            row = connection.execute(
                "SELECT id FROM reviews WHERE run_id = ? AND case_id = ?", (run_id, case_id)
            ).fetchone()
            return int(row["id"])

    def pending(self) -> list[ReviewItem]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM reviews WHERE status = 'pending' ORDER BY risk_score DESC, id"
            ).fetchall()
        return [self._row_to_item(row) for row in rows]

    def decide(self, item_id: int, *, reviewer: str, decision: str) -> None:
        if decision not in {"approve", "reject"}:
            raise ValueError("Decision must be approve or reject.")
        with self._connect() as connection:
            cursor = connection.execute(
                """UPDATE reviews SET status = 'resolved', reviewer = ?, decision = ?
                WHERE id = ? AND status = 'pending'""",
                (reviewer, decision, item_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(f"Pending review {item_id} was not found.")

    @staticmethod
    def _row_to_item(row: sqlite3.Row) -> ReviewItem:
        payload = dict(row)
        payload["payload"] = json.loads(payload["payload"])
        return ReviewItem(**payload)

    @staticmethod
    def serialize(item: ReviewItem) -> dict[str, Any]:
        return asdict(item)

