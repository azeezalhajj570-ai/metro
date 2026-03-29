# Smart Metro Assistance Web Platform

Smart Metro Assistance Web Platform is a graduation-level accessibility project that helps vulnerable passengers navigate a metro network more safely and independently. The system provides profile-aware route guidance, simplified step-by-step travel instructions, support recommendations for special-needs users, and an operations dashboard for tracking assistance activity.

## Project Objectives

- Support elderly passengers, children, deaf and mute users, and visually impaired travelers with adaptive guidance.
- Simplify metro navigation using profile-specific route recommendations instead of complex full-network maps.
- Log route requests, staff assistance requests, and SOS alerts for demonstration and analytics purposes.
- Provide a polished web interface suitable for mobile browsers, kiosk screens, and staff tablets.
- Keep the codebase modular, documented, and easy to explain during academic evaluation.

## System Architecture

The project is divided into four layers:

1. Request handling and page rendering in [app.py](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/app.py).
2. Route planning and accessibility-aware guidance in [src/planner.py](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/src/planner.py).
3. SQLite logging and dashboard metrics in [src/database.py](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/src/database.py).
4. Presentation layer in [templates/](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/templates) and [static/](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/static).

## Technologies Used

- Python 3.x
- Flask
- SQLite
- HTML5
- Tailwind CSS
- Chart.js

## Project Structure

```text
project/
|-- app.py
|-- requirements.txt
|-- readme.md
|-- AGENT.md
|-- data/
|   |-- metro_stations.json
|   `-- metro.db
|-- models/
|   `-- .gitkeep
|-- src/
|   |-- __init__.py
|   |-- planner.py
|   `-- database.py
|-- templates/
|   |-- base.html
|   |-- index.html
|   `-- dashboard.html
`-- static/
    |-- css/
    |   `-- styles.css
    `-- js/
        `-- app.js
```

## Core Features

- Accessibility-aware route planner with four user profiles
- Simplified step-by-step metro journey instructions
- Support notes for elevators, tactile guidance, visual alerts, and staff desks
- Assistance request logging for route guidance, staff help, and SOS alerts
- Admin dashboard with request analytics and recent activity history
- JSON API endpoints for route planning and station lookup

## Demo Network Data

The included dataset in [data/metro_stations.json](/c:/Users/pc/Desktop/UNI-PROJECTS/metro/data/metro_stations.json) contains:

- A small Riyadh-inspired metro station network
- Line, zone, elevator, tactile, family-area, and staff-desk metadata
- Profile definitions for elderly, children, visually impaired, and deaf and mute passengers
- Weighted edges used by the route planner to prefer more suitable paths

This sample data is designed for graduation-project demonstrations and can be expanded later with real station information or live APIs.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: define a custom Flask secret key for deployment:

```bash
set FLASK_SECRET_KEY=your-secret-key
```

## How to Run the System

Start the Flask application:

```bash
python app.py
```

Open:

- `http://127.0.0.1:5000` for the metro assistance planner
- `http://127.0.0.1:5000/dashboard` for the admin dashboard

## API Endpoints

- `GET /health`
- `GET /api/stations`
- `POST /api/plan`

Example JSON body for `POST /api/plan`:

```json
{
  "origin": "King Abdullah Financial District",
  "destination": "Riyadh Railway",
  "profile": "visually_impaired",
  "priority": "fewest_transfers"
}
```

## Demonstration Flow

1. Start the Flask application.
2. Open the planner page and choose an accessibility profile.
3. Select the origin and destination stations.
4. Generate the assistance plan and review the route, timing, and support notes.
5. Open the dashboard to show the stored request history and SOS analytics.

## Screenshots

- Home page screenshot: add a capture of the planner interface here.
- Dashboard screenshot: add a capture of the analytics page here.
- Mobile or kiosk screenshot: add a responsive-layout capture here.

## Academic Notes

- The project reflects the problem statement in the project report by focusing on inclusive transit assistance.
- The codebase is intentionally modular so the planning logic, persistence layer, and UI can be discussed separately.
- The current route planner is rule-based and can later be extended with live metro APIs, indoor positioning, or machine learning.
