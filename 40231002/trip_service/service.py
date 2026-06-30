from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from routing_service.service import Point, RoutingService

class TripStatus(str, Enum):
    REQUESTED = 'requested'
    DRIVER_ASSIGNED = 'driver_assigned'
    ROUTE_CALCULATED = 'route_calculated'
    COMPLETED = 'completed'
    PAID = 'paid'

@dataclass
class Trip:
    trip_id: str
    passenger_id: str
    origin: Point
    stops: List[Point]
    driver_id: Optional[str] = None
    status: TripStatus = TripStatus.REQUESTED
    distance_km: float = 0.0
    fare: float = 0.0
BASE_FARE = 1.5
PER_KM_RATE = 0.8

class TripService:

    def __init__(self, routing_service: Optional[RoutingService]=None) -> None:
        self._trips = {}
        self._routing = routing_service or RoutingService()

    def request_trip(self, trip_id: str, passenger_id: str, origin: Point, stops: List[Point]) -> Trip:
        if not stops:
            raise ValueError('trip must have at least one destination')
        trip = Trip(trip_id=trip_id, passenger_id=passenger_id, origin=origin, stops=stops)
        self._trips[trip_id] = trip
        return trip

    def assign_driver(self, trip_id: str, driver_id: str) -> Trip:
        trip = self._get(trip_id)
        trip.driver_id = driver_id
        trip.status = TripStatus.DRIVER_ASSIGNED
        return trip

    def calculate_route_and_fare(self, trip_id: str) -> Trip:
        trip = self._get(trip_id)
        _, distance_km = self._routing.calculate_route(trip.origin, trip.stops)
        trip.distance_km = distance_km
        trip.fare = round(BASE_FARE + PER_KM_RATE * distance_km, 2)
        trip.status = TripStatus.ROUTE_CALCULATED
        return trip

    def complete_trip(self, trip_id: str) -> Trip:
        trip = self._get(trip_id)
        if trip.status != TripStatus.ROUTE_CALCULATED:
            raise ValueError('trip must have route calculated before completion')
        trip.status = TripStatus.COMPLETED
        return trip

    def mark_paid(self, trip_id: str) -> Trip:
        trip = self._get(trip_id)
        if trip.status != TripStatus.COMPLETED:
            raise ValueError('trip must be completed before payment')
        trip.status = TripStatus.PAID
        return trip

    def _get(self, trip_id: str) -> Trip:
        trip = self._trips.get(trip_id)
        if trip is None:
            raise ValueError('trip not found')
        return trip
