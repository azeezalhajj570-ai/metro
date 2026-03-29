from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app import create_app
from src.database import get_dashboard_metrics, init_db


class SmartMetroAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        init_db(self.database_path)

        app = create_app(self.database_path)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_home_page_loads(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Generate an assistance plan", response.data)

    def test_api_plan_returns_route(self) -> None:
        response = self.client.post(
            "/api/plan",
            json={
                "origin": "King Abdullah Financial District",
                "destination": "Riyadh Railway",
                "profile": "elderly",
                "priority": "accessible",
                "request_type": "route_guidance",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        assert payload is not None
        self.assertIn("route", payload)
        self.assertGreaterEqual(len(payload["route"]), 2)

    def test_api_help_logs_request(self) -> None:
        baseline_metrics = get_dashboard_metrics(self.database_path)
        response = self.client.post(
            "/api/help",
            json={
                "traveler_name": "Demo User",
                "profile": "children",
                "origin": "National Museum",
                "destination": "National Museum",
                "priority": "balanced",
                "source_device": "kiosk",
                "request_type": "sos_alert",
                "notes": "Guardian separation drill.",
            },
        )

        self.assertEqual(response.status_code, 200)
        metrics = get_dashboard_metrics(self.database_path)
        self.assertEqual(metrics["total_requests"], baseline_metrics["total_requests"] + 1)
        self.assertEqual(metrics["sos_count"], baseline_metrics["sos_count"] + 1)

    def test_dashboard_loads(self) -> None:
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_login_page_loads(self) -> None:
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Operator session", response.data)

    def test_login_allows_dashboard_access(self) -> None:
        login_response = self.client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertIn(b"Management Decision Support Dashboard", login_response.data)


if __name__ == "__main__":
    unittest.main()
