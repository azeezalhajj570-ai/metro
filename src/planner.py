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
    has_elevator: bool
    has_staff_desk: bool
    family_waiting_area: bool
    tactile_guidance: bool


class RoutePlanner:
    def __init__(self, stations_path: Path) -> None:
        payload = json.loads(stations_path.read_text(encoding="utf-8"))
        self.stations: dict[str, Station] = {
            item["name"]: Station(**item) for item in payload["stations"]
        }
        self.edges: dict[str, list[dict[str, str | int]]] = payload["edges"]
        self.station_names = sorted(self.stations.keys())
        self.profile_catalog = payload["profiles"]

    def build_plan(self, origin: str, destination: str, profile: str, priority: str) -> dict[str, object]:
        if not origin or not destination:
            raise PlannerError("Please choose both the current station and the destination station.")
        if origin == destination:
            raise PlannerError("Origin and destination must be different stations.")
        if origin not in self.stations or destination not in self.stations:
            raise PlannerError("One of the selected stations does not exist in the demo metro network.")
        if profile not in self.profile_catalog:
            raise PlannerError("The selected accessibility profile is not supported.")

        route = self._shortest_path(origin, destination, profile, priority)
        steps = self._build_steps(route)
        summary = self._build_summary(route)
        support = self._profile_support(route, profile)

        return {
            "summary": summary,
            "estimated_minutes": self._estimate_minutes(route, profile),
            "transfer_count": max(len(route) - 2, 0),
            "route": route,
            "steps": steps,
            "support": support,
            "profile_label": self.profile_catalog[profile]["label"],
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
            base_minutes += 4
        elif priority == "fastest":
            base_minutes -= 0.5

        if profile == "elderly":
            if edge_type == "transfer":
                base_minutes += 3
            if not current_station.has_elevator or not neighbor_station.has_elevator:
                base_minutes += 5
        elif profile == "children":
            if edge_type == "transfer":
                base_minutes += 2
            if not neighbor_station.family_waiting_area:
                base_minutes += 1
        elif profile == "visually_impaired":
            if not current_station.tactile_guidance or not neighbor_station.tactile_guidance:
                base_minutes += 4
        elif profile == "deaf_mute":
            if edge_type == "transfer":
                base_minutes += 1

        return max(base_minutes, 1)

    def _build_steps(self, route: list[str]) -> list[str]:
        steps: list[str] = []
        for index, station_name in enumerate(route):
            station = self.stations[station_name]
            if index == 0:
                steps.append(
                    f"Start at {station.name} on the {station.line} in {station.zone}. Move to the clearly marked boarding area."
                )
                continue

            previous_station = self.stations[route[index - 1]]
            if previous_station.line == station.line:
                steps.append(f"Stay on the {station.line} and continue to {station.name}.")
            else:
                steps.append(
                    f"Transfer from the {previous_station.line} to the {station.line}, then continue to {station.name}."
                )

        final_station = self.stations[route[-1]]
        steps.append(
            f"Arrive at {final_station.name}. The nearest staff desk is {'available' if final_station.has_staff_desk else 'not listed in this demo'}, so request assistance if needed."
        )
        return steps

    def _build_summary(self, route: list[str]) -> str:
        start = self.stations[route[0]]
        end = self.stations[route[-1]]
        return f"{start.name} to {end.name} via {len(route)} guided stops"

    def _estimate_minutes(self, route: list[str], profile: str) -> int:
        total = 0.0
        for current, nxt in zip(route, route[1:]):
            edge = next(item for item in self.edges[current] if item["to"] == nxt)
            total += float(edge.get("minutes", 4))

        if profile == "elderly":
            total += 4
        elif profile == "children":
            total += 3
        elif profile == "visually_impaired":
            total += 5
        else:
            total += 2

        return round(total)

    def _profile_support(self, route: list[str], profile: str) -> list[str]:
        destination_station = self.stations[route[-1]]
        support = [self.profile_catalog[profile]["guidance"]]

        if profile == "elderly":
            support.append("Prefer elevators and longer dwell times when changing platforms.")
        elif profile == "children":
            support.append("Use color-based instructions and keep the child close to the family waiting area during transfers.")
        elif profile == "visually_impaired":
            support.append("Provide continuous audio prompts and confirm tactile paving before each platform move.")
        elif profile == "deaf_mute":
            support.append("Use visual stop alerts and the text-to-speech communication board for staff interaction.")

        support.append(
            f"Destination zone: {destination_station.zone}. Staff desk {'available' if destination_station.has_staff_desk else 'not confirmed'}."
        )
        return support
