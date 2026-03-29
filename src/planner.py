from __future__ import annotations

import heapq
import json
from dataclasses import dataclass
from pathlib import Path


class PlannerError(ValueError):
    """Raised when the route planner cannot create a valid assistance plan."""


@dataclass(slots=True)
class Station:
    name: str
    line: str
    zone: str
    beacon_zone: str
    landmark: str
    has_elevator: bool
    has_staff_desk: bool
    family_waiting_area: bool
    tactile_guidance: bool
    quiet_area: bool
    visual_alerts: bool
    seating: bool


class RoutePlanner:
    def __init__(self, stations_path: Path) -> None:
        payload = json.loads(stations_path.read_text(encoding="utf-8"))
        self.stations: dict[str, Station] = {
            item["name"]: Station(**item) for item in payload["stations"]
        }
        self.edges: dict[str, list[dict[str, str | int]]] = payload["edges"]
        self.station_names = sorted(self.stations.keys())
        self.profile_catalog: dict[str, dict[str, str]] = payload["profiles"]
        self.priority_options: dict[str, str] = payload["priority_options"]
        self.device_options: dict[str, str] = payload["device_options"]
        self.quick_actions: list[dict[str, str]] = payload["quick_actions"]
        self.station_cards = [self._station_card(name) for name in self.station_names[:6]]

    def build_plan(
        self,
        origin: str,
        destination: str,
        profile: str,
        priority: str,
        request_type: str = "route_guidance",
    ) -> dict[str, object]:
        if not origin or not destination:
            raise PlannerError("Please choose both the current station and the destination station.")
        if origin == destination and request_type == "route_guidance":
            raise PlannerError("Origin and destination must be different stations for route guidance.")
        if origin not in self.stations or destination not in self.stations:
            raise PlannerError("One of the selected stations does not exist in the demo metro network.")
        if profile not in self.profile_catalog:
            raise PlannerError("The selected accessibility profile is not supported.")
        if priority not in self.priority_options:
            raise PlannerError("The selected route priority is not supported.")

        route = [origin] if origin == destination else self._shortest_path(origin, destination, profile, priority)
        stations = [self.stations[name] for name in route]
        summary = self._build_summary(route, request_type)

        return {
            "summary": summary,
            "estimated_minutes": self._estimate_minutes(route, profile, request_type),
            "transfer_count": self._count_transfers(route),
            "route": route,
            "steps": self._build_steps(route, profile, request_type),
            "support": self._profile_support(route, profile, request_type),
            "profile_label": self.profile_catalog[profile]["label"],
            "profile_theme": self.profile_catalog[profile]["theme"],
            "origin_zone": stations[0].zone,
            "destination_zone": stations[-1].zone,
            "origin_beacon_zone": stations[0].beacon_zone,
            "staff_channel": self._staff_channel(stations[0], profile, request_type),
            "safety_notes": self._safety_notes(route, profile, request_type),
            "wristband": self._wristband_guidance(stations[0], profile),
            "communication_board": self._communication_board(profile),
        }

    def _station_card(self, name: str) -> dict[str, str]:
        station = self.stations[name]
        return {
            "name": station.name,
            "line": station.line,
            "zone": station.zone,
            "landmark": station.landmark,
            "beacon_zone": station.beacon_zone,
        }

    def _shortest_path(self, origin: str, destination: str, profile: str, priority: str) -> list[str]:
        queue: list[tuple[float, str, list[str]]] = [(0.0, origin, [origin])]
        best_cost: dict[str, float] = {origin: 0.0}

        while queue:
            cost, station_name, path = heapq.heappop(queue)
            if station_name == destination:
                return path

            for edge in self.edges.get(station_name, []):
                neighbor = str(edge["to"])
                next_cost = cost + self._edge_cost(station_name, neighbor, edge, profile, priority)
                if next_cost < best_cost.get(neighbor, float("inf")):
                    best_cost[neighbor] = next_cost
                    heapq.heappush(queue, (next_cost, neighbor, path + [neighbor]))

        raise PlannerError("No route was found between the selected stations in the demo network.")

    def _edge_cost(
        self,
        current: str,
        neighbor: str,
        edge: dict[str, str | int],
        profile: str,
        priority: str,
    ) -> float:
        base_minutes = float(edge.get("minutes", 4))
        edge_type = str(edge.get("type", "ride"))
        current_station = self.stations[current]
        neighbor_station = self.stations[neighbor]

        if priority == "fewest_transfers" and edge_type == "transfer":
            base_minutes += 5
        elif priority == "accessible" and edge_type == "transfer":
            base_minutes += 2
        elif priority == "fastest":
            base_minutes -= 0.5

        if profile == "elderly":
            if edge_type == "transfer":
                base_minutes += 3
            if not current_station.has_elevator or not neighbor_station.has_elevator:
                base_minutes += 5
            if not neighbor_station.seating:
                base_minutes += 1
        elif profile == "children":
            if edge_type == "transfer":
                base_minutes += 2
            if not neighbor_station.family_waiting_area:
                base_minutes += 2
            if not neighbor_station.visual_alerts:
                base_minutes += 1
        elif profile == "visually_impaired":
            if not current_station.tactile_guidance or not neighbor_station.tactile_guidance:
                base_minutes += 5
            if edge_type == "transfer":
                base_minutes += 2
        elif profile == "deaf_mute":
            if not neighbor_station.visual_alerts:
                base_minutes += 4
            if edge_type == "transfer":
                base_minutes += 1.5

        return max(base_minutes, 1)

    def _build_steps(self, route: list[str], profile: str, request_type: str) -> list[dict[str, str]]:
        profile_hint = self.profile_catalog[profile]["step_style"]
        steps: list[dict[str, str]] = []

        for index, station_name in enumerate(route):
            station = self.stations[station_name]
            if index == 0:
                steps.append(
                    {
                        "title": f"Begin at {station.name}",
                        "detail": (
                            f"Move to the assisted boarding point near {station.landmark}. "
                            f"Beacon zone {station.beacon_zone} is the reference point for staff support."
                        ),
                        "hint": profile_hint,
                    }
                )
                continue

            previous_station = self.stations[route[index - 1]]
            if previous_station.line == station.line:
                detail = f"Stay on the {station.line} and continue to {station.name}."
            else:
                detail = (
                    f"Transfer from the {previous_station.line} to the {station.line}. "
                    f"Follow the marked accessible path toward {station.landmark}."
                )

            steps.append(
                {
                    "title": f"Reach {station.name}",
                    "detail": detail,
                    "hint": self._station_hint(station, profile),
                }
            )

        final_station = self.stations[route[-1]]
        closing_detail = (
            f"Arrive in {final_station.zone}. Staff desk is "
            f"{'available' if final_station.has_staff_desk else 'not listed in this demo'} near {final_station.landmark}."
        )
        if request_type != "route_guidance":
            closing_detail = (
                f"Hold position near {final_station.landmark}. Your {request_type.replace('_', ' ')} signal is tagged to "
                f"{final_station.beacon_zone} for operator follow-up."
            )
        steps.append(
            {
                "title": f"Finish at {final_station.name}",
                "detail": closing_detail,
                "hint": "Use the persistent Help button if conditions around you change.",
            }
        )
        return steps

    def _station_hint(self, station: Station, profile: str) -> str:
        hints = []
        if profile == "elderly" and station.seating:
            hints.append("Seating available for a short rest.")
        if profile == "children" and station.family_waiting_area:
            hints.append("Family waiting area available.")
        if profile == "visually_impaired" and station.tactile_guidance:
            hints.append("Tactile guidance continues through this platform.")
        if profile == "deaf_mute" and station.visual_alerts:
            hints.append("Platform visual alerts are active.")
        if station.has_elevator:
            hints.append("Elevator access available.")
        return " ".join(hints) or "Ask staff for localized support if this station feels crowded."

    def _build_summary(self, route: list[str], request_type: str) -> str:
        start = self.stations[route[0]]
        end = self.stations[route[-1]]
        if request_type == "route_guidance":
            return f"{start.name} to {end.name} via {len(route)} guided stops"
        return f"{request_type.replace('_', ' ').title()} from {start.zone} linked to {end.name}"

    def _estimate_minutes(self, route: list[str], profile: str, request_type: str) -> int:
        if len(route) == 1:
            return 2 if request_type == "sos_alert" else 4

        total = 0.0
        for current, nxt in zip(route, route[1:]):
            edge = next(item for item in self.edges[current] if item["to"] == nxt)
            total += float(edge.get("minutes", 4))

        profile_buffer = {
            "elderly": 5,
            "children": 4,
            "visually_impaired": 6,
            "deaf_mute": 3,
        }
        total += profile_buffer.get(profile, 3)
        if request_type == "staff_assistance":
            total = max(total - 2, 3)
        elif request_type == "sos_alert":
            total = max(total - 4, 2)
        return round(total)

    def _count_transfers(self, route: list[str]) -> int:
        transfers = 0
        for current, nxt in zip(route, route[1:]):
            if self.stations[current].line != self.stations[nxt].line:
                transfers += 1
        return transfers

    def _profile_support(self, route: list[str], profile: str, request_type: str) -> list[str]:
        destination_station = self.stations[route[-1]]
        support = [self.profile_catalog[profile]["guidance"]]

        profile_notes = {
            "elderly": "Prefer elevators, calmer transfers, and rest-enabled stations wherever possible.",
            "children": "Use icon-led directions, guardian checkpoints, and high-visibility waiting areas during transfers.",
            "visually_impaired": "Keep audio prompts active and confirm tactile paving before every platform move.",
            "deaf_mute": "Use the text board, visual stop alerts, and haptic wristband confirmations when available.",
        }
        support.append(profile_notes[profile])

        if request_type == "staff_assistance":
            support.append("The nearest staff tablet should receive a non-emergency assistance ping for this station zone.")
        elif request_type == "sos_alert":
            support.append("SOS escalation should be treated as a silent high-priority alert linked to the wristband or kiosk zone.")

        support.append(
            f"Destination zone: {destination_station.zone}. Staff desk "
            f"{'available' if destination_station.has_staff_desk else 'not confirmed'}."
        )
        return support

    def _safety_notes(self, route: list[str], profile: str, request_type: str) -> list[str]:
        origin = self.stations[route[0]]
        destination = self.stations[route[-1]]
        notes = [
            f"Nearest beacon reference: {origin.beacon_zone}.",
            f"Staff dispatch default: {self._staff_channel(origin, profile, request_type)}.",
        ]
        if profile == "children":
            notes.append("If a guardian is missing, hold the child at the nearest family waiting area before moving again.")
        if profile == "visually_impaired":
            notes.append("Maintain spoken confirmation before stairs, escalators, or platform edge changes.")
        if request_type == "sos_alert":
            notes.append(f"Escalate using silent alert flow and meet the user at {destination.landmark}.")
        return notes

    def _wristband_guidance(self, station: Station, profile: str) -> dict[str, str]:
        return {
            "zone": station.beacon_zone,
            "status": "Localized indoor tracking active through BLE/Wi-Fi beacon estimation.",
            "feedback": self.profile_catalog[profile]["feedback"],
            "fallback": "If beacon coverage drops, instruct the traveler to scan the nearest checkpoint QR marker.",
        }

    def _staff_channel(self, station: Station, profile: str, request_type: str) -> str:
        urgency = "priority" if request_type == "sos_alert" else "standard"
        return f"{urgency} desk dispatch for {station.zone} ({profile.replace('_', ' ')})"

    def _communication_board(self, profile: str) -> list[str]:
        messages = [
            "I need help reaching the correct platform.",
            "Please guide me to the nearest elevator.",
            "I am waiting near the beacon checkpoint shown on screen.",
        ]
        if profile == "deaf_mute":
            messages.append("Please respond using text or visual directions.")
        elif profile == "children":
            messages.append("Please contact my guardian or station safety team.")
        return messages
