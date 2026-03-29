# Smart Metro Assistance Web Platform

Smart Metro Assistance is a graduation-ready Flask platform that demonstrates how vulnerable passengers can receive accessible metro guidance, rapid staff support, and GPS-free safety coverage inside large underground stations.

The prototype is modeled around a Riyadh-inspired network and focuses on four traveler groups:

- elderly passengers
- children and minors
- visually impaired users
- deaf and mute users

It also includes an operator dashboard for metro administrators who need visibility into SOS activity, zone pressure, and profile-specific demand.

The app now ships with seeded demo data so the dashboard is populated on first run, plus a simple operator login flow for protected admin access.

## What the platform demonstrates

- Adaptive route planning with profile-specific guidance and accessibility-aware weighting
- Immediate help and SOS request logging linked to indoor beacon zones
- Mobile, kiosk, and staff-tablet friendly web experience
- Conceptual smart wristband integration for underground localization and haptic alerts
- Dashboard analytics for requests by type, profile, and station zone

## Stack

- Python 3
- Flask
- SQLite
- HTML5
- Tailwind CSS via CDN
- Vanilla JavaScript
- Chart.js

## Project structure

```text
metro/
|-- app.py
|-- requirements.txt
|-- readme.md
|-- AGENT.md
|-- data/
|   `-- metro_stations.json
|-- models/
|   `-- .gitkeep
|-- src/
|   |-- __init__.py
|   |-- database.py
|   `-- planner.py
|-- static/
|   |-- css/
|   |   `-- styles.css
|   `-- js/
|       `-- app.js
|-- templates/
|   |-- base.html
|   |-- dashboard.html
|   `-- index.html
`-- tests/
    `-- test_app.py
```

## Key pages

- `/` traveler hub for route planning, accessibility profile selection, quick staff help, and SOS triggers
- `/login` operator login page
- `/dashboard` operator dashboard for analytics and recent assistance activity

## Seeded demo access

- Default operator username: `admin`
- Default operator password: `admin123`

This seeded account is intended for prototype demonstrations only.

## API endpoints

- `GET /health`
- `GET /api/stations`
- `POST /api/plan`
- `POST /api/help`

Example body for `POST /api/plan`:

```json
{
  "origin": "King Abdullah Financial District",
  "destination": "Riyadh Railway",
  "profile": "visually_impaired",
  "priority": "accessible",
  "request_type": "route_guidance"
}
```

Example body for `POST /api/help`:

```json
{
  "traveler_name": "Demo User",
  "profile": "elderly",
  "origin": "National Museum",
  "destination": "National Museum",
  "priority": "balanced",
  "source_device": "kiosk",
  "request_type": "sos_alert",
  "notes": "User feels unwell near the central gate."
}
```

## Run locally

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

4. Open `http://127.0.0.1:5000`.

## Demo flow

1. Open the traveler hub and choose an accessibility profile.
2. Select an origin, destination, route priority, and access channel.
3. Generate a plan and review the route summary, safety notes, and communication prompts.
4. Trigger a quick assistance or SOS action to simulate staff escalation.
5. Open the dashboard to review the logged request activity and zone analytics.

## Current prototype boundaries

- The station network is a curated demo dataset, not a live Riyadh Metro feed.
- Indoor localization is modeled through beacon-zone metadata and workflow logic, not live hardware telemetry.
- The wristband integration is conceptual and represented in software output for demonstration purposes.
- Authentication is a simple session-based prototype login, not a production identity system.

These boundaries are intentional so the project remains explainable, testable, and suitable for academic defense or prototype presentations.
