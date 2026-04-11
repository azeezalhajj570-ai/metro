from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from src.database import (
    AssistanceRequestRecord,
    authenticate_user,
    get_dashboard_metrics,
    get_recent_requests,
    init_db,
    insert_request,
)
from src.planner import PlannerError, RoutePlanner


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "metro.db"
STATIONS_PATH = BASE_DIR / "data" / "metro_stations.json"


def create_app(database_path_override: Path | None = None) -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "change-this-secret-key")
    app.config["DATABASE_PATH"] = database_path_override or DATABASE_PATH

    init_db(app.config["DATABASE_PATH"])
    planner = RoutePlanner(STATIONS_PATH)

    def database_path() -> Path:
        return Path(app.config["DATABASE_PATH"])

    def current_user() -> dict[str, str] | None:
        user = session.get("admin_user")
        return user if isinstance(user, dict) else None

    @app.context_processor
    def inject_shell_context() -> dict[str, object]:
        return {
            "admin_user": current_user(),
            "is_authenticated": current_user() is not None,
        }

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
            "source_device": "mobile_browser",
            "notes": "",
        }

        if request.method == "POST":
            for key, fallback in form_data.items():
                form_data[key] = (request.form.get(key) or "").strip() or fallback

            try:
                travel_plan = planner.build_plan(
                    origin=form_data["origin"],
                    destination=form_data["destination"],
                    profile=form_data["profile"],
                    priority=form_data["priority"],
                    request_type=form_data["request_type"],
                )
                insert_request(
                    database_path(),
                    AssistanceRequestRecord(
                        traveler_name=form_data["traveler_name"] or "Guest User",
                        profile=form_data["profile"],
                        origin=form_data["origin"],
                        destination=form_data["destination"],
                        request_type=form_data["request_type"],
                        priority=form_data["priority"],
                        source_device=form_data["source_device"],
                        zone=travel_plan["origin_zone"],
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
                    station_cards=planner.station_cards,
                    priority_options=planner.priority_options,
                    device_options=planner.device_options,
                    quick_actions=planner.quick_actions,
                    dashboard_snapshot=get_dashboard_metrics(database_path()),
                )

        return render_template(
            "index.html",
            error_message=None,
            plan=travel_plan,
            form_data=form_data,
            stations=planner.station_names,
            profiles=planner.profile_catalog,
            station_cards=planner.station_cards,
            priority_options=planner.priority_options,
            device_options=planner.device_options,
            quick_actions=planner.quick_actions,
            dashboard_snapshot=get_dashboard_metrics(database_path()),
        )

    @app.route("/dashboard")
    def dashboard():
        if not current_user():
            return redirect(url_for("login", next=request.path))
        metrics = get_dashboard_metrics(database_path())
        recent_requests = get_recent_requests(database_path(), limit=12)
        return render_template(
            "dashboard.html",
            metrics=metrics,
            recent_requests=recent_requests,
            profiles=planner.profile_catalog,
        )

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error_message = None
        next_url = request.args.get("next") or request.form.get("next") or url_for("dashboard")

        if request.method == "POST":
            username = (request.form.get("username") or "").strip()
            password = request.form.get("password") or ""
            user = authenticate_user(database_path(), username, password)
            if user:
                session["admin_user"] = user
                return redirect(next_url)
            error_message = "Invalid username or password."

        return render_template("login.html", error_message=error_message, next_url=next_url)

    @app.post("/logout")
    def logout():
        session.pop("admin_user", None)
        return redirect(url_for("index"))

    @app.post("/api/plan")
    def api_plan():
        payload = request.get_json(silent=True) or {}

        try:
            result = planner.build_plan(
                origin=(payload.get("origin") or "").strip(),
                destination=(payload.get("destination") or "").strip(),
                profile=(payload.get("profile") or "elderly").strip(),
                priority=(payload.get("priority") or "balanced").strip(),
                request_type=(payload.get("request_type") or "route_guidance").strip(),
            )
            return jsonify(result)
        except PlannerError as exc:
            return jsonify({"error": str(exc)}), 400

    @app.post("/api/help")
    def api_help():
        payload = request.get_json(silent=True) or {}
        request_type = (payload.get("request_type") or "staff_assistance").strip()
        origin = (payload.get("origin") or "").strip()
        destination = (payload.get("destination") or origin).strip()
        profile = (payload.get("profile") or "elderly").strip()
        priority = (payload.get("priority") or "balanced").strip()
        traveler_name = (payload.get("traveler_name") or "Station User").strip()
        source_device = (payload.get("source_device") or "kiosk").strip()
        notes = (payload.get("notes") or "").strip()

        try:
            plan = planner.build_plan(
                origin=origin,
                destination=destination,
                profile=profile,
                priority=priority,
                request_type=request_type,
            )
            record = AssistanceRequestRecord(
                traveler_name=traveler_name,
                profile=profile,
                origin=origin,
                destination=destination,
                request_type=request_type,
                priority=priority,
                source_device=source_device,
                zone=plan["origin_zone"],
                notes=notes or "Triggered from quick assistance action.",
                route_summary=plan["summary"],
            )
            insert_request(database_path(), record)
        except PlannerError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(
            {
                "status": "queued",
                "message": "Nearest staff team notified for the selected station zone.",
                "zone": plan["origin_zone"],
                "request_type": request_type,
                "recommended_channel": plan["staff_channel"],
            }
        )

    @app.get("/api/stations")
    def api_stations():
        return jsonify(
            {
                "stations": planner.station_names,
                "profiles": planner.profile_catalog,
                "devices": planner.device_options,
                "priorities": planner.priority_options,
            }
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/refresh")
    def refresh():
        return redirect(url_for("index"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5002)
