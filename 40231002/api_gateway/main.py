from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from user_service.service import UserService
from trip_service.service import TripService
from payment_service.service import PaymentService
from wallet_service.service import WalletService
from routing_service.service import Point, RoutingService
app = FastAPI(title='Taxi App API Gateway')
routing_service = RoutingService()
user_service = UserService()
trip_service = TripService(routing_service=routing_service)
payment_service = PaymentService()
wallet_service = WalletService()

class RegisterUserRequest(BaseModel):
    user_id: str
    name: str
    phone: str
    role: str

class PointModel(BaseModel):
    lat: float
    lng: float

class RequestTripRequest(BaseModel):
    trip_id: str
    passenger_id: str
    origin: PointModel
    stops: List[PointModel]

class InitiatePaymentRequest(BaseModel):
    payment_id: str
    trip_id: str
    amount: float
    currency: str
    wallet_address: str

@app.post('/users/register')
def register_user(req: RegisterUserRequest):
    try:
        user = user_service.register(req.user_id, req.name, req.phone, req.role)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/trips/request')
def request_trip(req: RequestTripRequest):
    try:
        origin = Point(req.origin.lat, req.origin.lng)
        stops = [Point(s.lat, s.lng) for s in req.stops]
        trip = trip_service.request_trip(req.trip_id, req.passenger_id, origin, stops)
        trip_service.calculate_route_and_fare(req.trip_id)
        return trip_service._get(req.trip_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/trips/{trip_id}/complete')
def complete_trip(trip_id: str):
    try:
        return trip_service.complete_trip(trip_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/payments/initiate')
def initiate_payment(req: InitiatePaymentRequest):
    try:
        return payment_service.initiate_payment(req.payment_id, req.trip_id, req.amount, req.currency, req.wallet_address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/payments/{payment_id}/confirm')
def confirm_payment(payment_id: str):
    try:
        return payment_service.confirm_payment(payment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/health')
def health():
    return {'status': 'ok'}
