# AGENT.md

## Project Mission

Build and maintain a graduation-ready smart metro assistance platform for vulnerable passengers using Flask, SQLite, modular Python services, and an accessible demonstration UI.

## Engineering Guidelines

- Keep the documentation aligned with the code after every meaningful change.
- Preserve the modular architecture inside `src/` so the planning, data, and dashboard logic remain easy to explain during evaluation.
- Favor readable, university-presentable code over unnecessary complexity.
- Maintain an accessible, professional interface suitable for mobile, kiosk, and desktop demonstrations.
- Keep sample station data and assistance flows realistic enough to support presentations and screenshots.

## Operating Notes

- Run the Flask app with `python app.py`.
- Optional deployment setting: define `FLASK_SECRET_KEY` to override the default development secret.
- Assistance logs are stored in `data/metro.db`.
- Station topology, profile configuration, and demo indoor beacon zones are stored in `data/metro_stations.json`.
- The database seeds demo requests and a default operator account on first run.
- Demo operator credentials: `admin` / `admin123`.
- Quick help actions use `POST /api/help`; route planning uses `POST /api/plan`.

## Documentation Rule

Whenever project behavior, setup, file structure, or usage changes, update `readme.md` and this file in the same work session.
