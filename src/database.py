from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AssistanceRequestRecord:
    traveler_name: str
    profile: str
    origin: str
    destination: str
    request_type: str
    priority: str
    notes: str
    route_summary: str


def init_db(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS assistance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                traveler_name TEXT NOT NULL,
                profile TEXT NOT NULL,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                request_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                notes TEXT,
                route_summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()


def insert_request(database_path: Path, record: AssistanceRequestRecord) -> None:
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO assistance_requests (
                traveler_name,
                profile,
                origin,
                destination,
                request_type,
                priority,
                notes,
                route_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.traveler_name,
                record.profile,
                record.origin,
                record.destination,
                record.request_type,
                record.priority,
                record.notes,
                record.route_summary,
            ),
        )
        connection.commit()


def get_dashboard_metrics(database_path: Path) -> dict[str, int | float | str]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        total_requests = connection.execute(
            "SELECT COUNT(*) AS count FROM assistance_requests"
        ).fetchone()["count"]
        sos_count = connection.execute(
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE request_type = 'sos_alert'"
        ).fetchone()["count"]
        guided_count = connection.execute(
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE request_type = 'route_guidance'"
        ).fetchone()["count"]
        high_priority_count = connection.execute(
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE priority = 'fastest'"
        ).fetchone()["count"]

        top_profile_row = connection.execute(
            """
            SELECT profile, COUNT(*) AS count
            FROM assistance_requests
            GROUP BY profile
            ORDER BY count DESC, profile ASC
            LIMIT 1
            """
        ).fetchone()

    sos_rate = round((sos_count / total_requests) * 100, 1) if total_requests else 0.0
    return {
        "total_requests": total_requests,
        "sos_count": sos_count,
        "guided_count": guided_count,
        "high_priority_count": high_priority_count,
        "sos_rate": sos_rate,
        "top_profile": top_profile_row["profile"].replace("_", " ").title() if top_profile_row else "No data",
    }


def get_recent_requests(database_path: Path, limit: int = 10) -> list[sqlite3.Row]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                id,
                traveler_name,
                profile,
                origin,
                destination,
                request_type,
                priority,
                route_summary,
                created_at
            FROM assistance_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return rows
