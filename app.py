from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for

from src.database import (
    AssistanceRequestRecord,
    get_dashboard_metrics,
    get_recent_requests,
    init_db,
    insert_request,
)
from src.planner import PlannerError, RoutePlanner


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "metro.db"
STATIONS_PATH = BASE_DIR / "data" / "metro_stations.json"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
    app.config["DATABASE_PATH"] = DATABASE_PATH

    init_db(DATABASE_PATH)
    planner = RoutePlanner(STATIONS_PATH)

    @app.route("/", methods=["GET", "POST"])
    def index():
        travel_plan = None
        form_data = {
            "traveler_name": "",
            "profile": "elderly",
            "origin": "",
            "destination": "",
            "priority": "balanced",
            "request_type": "route_guidance",
            "notes": "",
        }

        if request.method == "POST":
            for key in form_data:
                form_data[key] = (request.form.get(key) or "").strip() or form_data[key]

            try:
                travel_plan = planner.build_plan(
                    origin=form_data["origin"],
                    destination=form_data["destination"],
                    profile=form_data["profile"],
                    priority=form_data["priority"],
                )
                insert_request(
                    DATABASE_PATH,
                    AssistanceRequestRecord(
                        traveler_name=form_data["traveler_name"] or "Guest User",
                        profile=form_data["profile"],
                        origin=form_data["origin"],
                        destination=form_data["destination"],
                        request_type=form_data["request_type"],
                        priority=form_data["priority"],
                        notes=form_data["notes"],
                        route_summary=travel_plan["summary"],
                    ),
                )
            except PlannerError as exc:
                return render_template(
                    "index.html",
                    error_message=str(exc),
                    plan=None,
                    form_data=form_data,
                    stations=planner.station_names,
                    profiles=planner.profile_catalog,
                )

        return render_template(
            "index.html",
            error_message=None,
            plan=travel_plan,
            form_data=form_data,
            stations=planner.station_names,
            profiles=planner.profile_catalog,
        )

    @app.route("/dashboard")
    def dashboard():
        metrics = get_dashboard_metrics(DATABASE_PATH)
        recent_requests = get_recent_requests(DATABASE_PATH, limit=12)
        return render_template(
            "dashboard.html",
            metrics=metrics,
            recent_requests=recent_requests,
        )

    @app.route("/api/plan", methods=["POST"])
    def api_plan():
        payload = request.get_json(silent=True) or {}

        try:
            result = planner.build_plan(
                origin=(payload.get("origin") or "").strip(),
                destination=(payload.get("destination") or "").strip(),
                profile=(payload.get("profile") or "elderly").strip(),
                priority=(payload.get("priority") or "balanced").strip(),
            )
            return jsonify(result)
        except PlannerError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.route("/api/stations")
    def api_stations():
        return jsonify(
            {
                "stations": planner.station_names,
                "profiles": planner.profile_catalog,
            }
        )

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/refresh")
    def refresh():
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
