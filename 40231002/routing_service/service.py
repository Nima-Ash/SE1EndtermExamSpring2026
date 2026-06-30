from dataclasses import dataclass
from typing import List, Tuple
import math

@dataclass
class Point:
    lat: float
    lng: float

def _haversine_km(a: Point, b: Point) -> float:
    R = 6371.0
    phi1, phi2 = (math.radians(a.lat), math.radians(b.lat))
    dphi = math.radians(b.lat - a.lat)
    dlambda = math.radians(b.lng - a.lng)
    h = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

class RoutingService:

    def calculate_route(self, origin: Point, stops: List[Point]) -> Tuple[List[Point], float]:
        if not stops:
            raise ValueError('at least one stop is required')
        remaining = stops.copy()
        current = origin
        ordered_route: List[Point] = []
        total_distance = 0.0
        while remaining:
            nearest = min(remaining, key=lambda p: _haversine_km(current, p))
            total_distance += _haversine_km(current, nearest)
            ordered_route.append(nearest)
            current = nearest
            remaining.remove(nearest)
        return (ordered_route, round(total_distance, 3))

    def estimate_duration_minutes(self, distance_km: float, avg_speed_kmh: float=30.0) -> float:
        if avg_speed_kmh <= 0:
            raise ValueError('avg_speed_kmh must be positive')
        return round(distance_km / avg_speed_kmh * 60, 2)
