from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from werkzeug.security import check_password_hash, generate_password_hash


@dataclass(slots=True)
class AssistanceRequestRecord:
    traveler_name: str
    profile: str
    origin: str
    destination: str
    request_type: str
    priority: str
    source_device: str
    zone: str
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
                source_device TEXT NOT NULL,
                zone TEXT NOT NULL,
                notes TEXT,
                route_summary TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        columns = {
            row[1]
            for row in connection.execute("PRAGMA table_info(assistance_requests)").fetchall()
        }
        if "source_device" not in columns:
            connection.execute(
                "ALTER TABLE assistance_requests ADD COLUMN source_device TEXT NOT NULL DEFAULT 'mobile_browser'"
            )
        if "zone" not in columns:
            connection.execute(
                "ALTER TABLE assistance_requests ADD COLUMN zone TEXT NOT NULL DEFAULT 'Unknown Zone'"
            )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'operator',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        _seed_users(connection)
        _seed_requests(connection)
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
                source_device,
                zone,
                notes,
                route_summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.traveler_name,
                record.profile,
                record.origin,
                record.destination,
                record.request_type,
                record.priority,
                record.source_device,
                record.zone,
                record.notes,
                record.route_summary,
            ),
        )
        connection.commit()


def get_dashboard_metrics(database_path: Path) -> dict[str, object]:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        total_requests = _count(connection, "SELECT COUNT(*) AS count FROM assistance_requests")
        sos_count = _count(
            connection,
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE request_type = 'sos_alert'",
        )
        guided_count = _count(
            connection,
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE request_type = 'route_guidance'",
        )
        staff_help_count = _count(
            connection,
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE request_type = 'staff_assistance'",
        )
        kiosk_count = _count(
            connection,
            "SELECT COUNT(*) AS count FROM assistance_requests WHERE source_device = 'kiosk'",
        )

        top_profile_row = connection.execute(
            """
            SELECT profile, COUNT(*) AS count
            FROM assistance_requests
            GROUP BY profile
            ORDER BY count DESC, profile ASC
            LIMIT 1
            """
        ).fetchone()

        busiest_zone_row = connection.execute(
            """
            SELECT zone, COUNT(*) AS count
            FROM assistance_requests
            GROUP BY zone
            ORDER BY count DESC, zone ASC
            LIMIT 1
            """
        ).fetchone()

        profile_breakdown = connection.execute(
            """
            SELECT profile, COUNT(*) AS count
            FROM assistance_requests
            GROUP BY profile
            ORDER BY count DESC, profile ASC
            """
        ).fetchall()

        zone_breakdown = connection.execute(
            """
            SELECT zone, COUNT(*) AS count
            FROM assistance_requests
            GROUP BY zone
            ORDER BY count DESC, zone ASC
            LIMIT 5
            """
        ).fetchall()

    sos_rate = round((sos_count / total_requests) * 100, 1) if total_requests else 0.0
    return {
        "total_requests": total_requests,
        "sos_count": sos_count,
        "guided_count": guided_count,
        "staff_help_count": staff_help_count,
        "kiosk_count": kiosk_count,
        "sos_rate": sos_rate,
        "top_profile": top_profile_row["profile"].replace("_", " ").title() if top_profile_row else "No data",
        "busiest_zone": busiest_zone_row["zone"] if busiest_zone_row else "No data",
        "profile_breakdown": [dict(row) for row in profile_breakdown],
        "zone_breakdown": [dict(row) for row in zone_breakdown],
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
                source_device,
                zone,
                route_summary,
                created_at
            FROM assistance_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return rows


def authenticate_user(database_path: Path, username: str, password: str) -> dict[str, str] | None:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        row = connection.execute(
            """
            SELECT id, full_name, username, password_hash, role
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

    if row and check_password_hash(row["password_hash"], password):
        return {
            "id": str(row["id"]),
            "full_name": row["full_name"],
            "username": row["username"],
            "role": row["role"],
        }
    return None


def _count(connection: sqlite3.Connection, query: str) -> int:
    return int(connection.execute(query).fetchone()[0])


def _seed_users(connection: sqlite3.Connection) -> None:
    existing = _count(connection, "SELECT COUNT(*) FROM users")
    if existing:
        return

    connection.execute(
        """
        INSERT INTO users (full_name, username, password_hash, role)
        VALUES (?, ?, ?, ?)
        """,
        (
            "Metro Control Supervisor",
            "admin",
            generate_password_hash("admin123"),
            "administrator",
        ),
    )


def _seed_requests(connection: sqlite3.Connection) -> None:
    existing = _count(connection, "SELECT COUNT(*) FROM assistance_requests")
    if existing:
        return

    demo_requests = [
        (
            "Fatimah Al-Harbi",
            "elderly",
            "King Abdullah Financial District",
            "National Museum",
            "route_guidance",
            "accessible",
            "mobile_browser",
            "North Hub",
            "Requested elevator-friendly route during morning travel.",
            "King Abdullah Financial District to National Museum via 4 guided stops",
        ),
        (
            "Child Safety Drill",
            "children",
            "National Museum",
            "National Museum",
            "staff_assistance",
            "balanced",
            "kiosk",
            "Central Riyadh",
            "Guardian separation simulation near museum-facing central gate.",
            "Staff Assistance from Central Riyadh linked to National Museum",
        ),
        (
            "Amina Hassan",
            "visually_impaired",
            "Qasr Al Hokm",
            "Riyadh Railway",
            "route_guidance",
            "accessible",
            "station_tablet",
            "Historic Core",
            "Requested audio-first route with tactile continuity notes.",
            "Qasr Al Hokm to Riyadh Railway via 3 guided stops",
        ),
        (
            "Silent Alert Demo",
            "deaf_mute",
            "Olaya-Batha",
            "Olaya-Batha",
            "sos_alert",
            "fastest",
            "wristband",
            "Central Riyadh",
            "Prototype SOS trigger from wristband demonstration.",
            "Sos Alert from Central Riyadh linked to Olaya-Batha",
        ),
    ]

    connection.executemany(
        """
        INSERT INTO assistance_requests (
            traveler_name,
            profile,
            origin,
            destination,
            request_type,
            priority,
            source_device,
            zone,
            notes,
            route_summary
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_requests,
    )
