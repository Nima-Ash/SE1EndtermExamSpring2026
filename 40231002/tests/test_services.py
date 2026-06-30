import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from user_service.service import UserService
from trip_service.service import TripService, TripStatus
from payment_service.service import PaymentService, PaymentStatus
from wallet_service.service import WalletService
from routing_service.service import RoutingService, Point

def test_register_and_login_user():
    svc = UserService()
    user = svc.register('u1', 'Ali', '0912000', 'passenger')
    assert user.user_id == 'u1'
    assert not user.is_authenticated
    logged_in = svc.login('u1')
    assert logged_in.is_authenticated

def test_register_duplicate_user_raises():
    svc = UserService()
    svc.register('u1', 'Ali', '0912000', 'passenger')
    with pytest.raises(ValueError):
        svc.register('u1', 'Ali2', '0912001', 'driver')

def test_register_invalid_role_raises():
    svc = UserService()
    with pytest.raises(ValueError):
        svc.register('u2', 'Sara', '0912002', 'admin')

def test_routing_multi_destination_orders_by_distance():
    rs = RoutingService()
    origin = Point(35.7, 51.4)
    stops = [Point(35.71, 51.41), Point(35.705, 51.405)]
    route, distance = rs.calculate_route(origin, stops)
    assert len(route) == 2
    assert distance > 0
    assert route[0] == Point(35.705, 51.405)

def test_routing_requires_at_least_one_stop():
    rs = RoutingService()
    with pytest.raises(ValueError):
        rs.calculate_route(Point(0, 0), [])

def test_full_trip_lifecycle():
    ts = TripService()
    origin = Point(35.7, 51.4)
    stops = [Point(35.71, 51.41)]
    trip = ts.request_trip('t1', 'u1', origin, stops)
    assert trip.status == TripStatus.REQUESTED
    ts.assign_driver('t1', 'd1')
    ts.calculate_route_and_fare('t1')
    trip = ts._get('t1')
    assert trip.fare > 0
    assert trip.status == TripStatus.ROUTE_CALCULATED
    completed = ts.complete_trip('t1')
    assert completed.status == TripStatus.COMPLETED
    paid = ts.mark_paid('t1')
    assert paid.status == TripStatus.PAID

def test_complete_trip_before_route_raises():
    ts = TripService()
    ts.request_trip('t2', 'u1', Point(0, 0), [Point(1, 1)])
    with pytest.raises(ValueError):
        ts.complete_trip('t2')

def test_crypto_payment_confirm_flow():
    ps = PaymentService()
    payment = ps.initiate_payment('p1', 't1', 25.5, 'USDT', '0xABC123')
    assert payment.status == PaymentStatus.PENDING
    confirmed = ps.confirm_payment('p1')
    assert confirmed.status == PaymentStatus.CONFIRMED
    assert confirmed.tx_hash != ''

def test_unsupported_currency_raises():
    ps = PaymentService()
    with pytest.raises(ValueError):
        ps.initiate_payment('p2', 't1', 10, 'DOGE', '0xABC')

def test_wallet_deposit_withdraw():
    ws = WalletService()
    ws.create_wallet('driver1')
    ws.deposit('driver1', 50)
    wallet = ws.get_wallet('driver1')
    assert wallet.balance == 50
    ws.withdraw('driver1', 20)
    assert ws.get_wallet('driver1').balance == 30

def test_wallet_insufficient_balance_raises():
    ws = WalletService()
    ws.create_wallet('driver2')
    with pytest.raises(ValueError):
        ws.withdraw('driver2', 10)

def test_settle_trip_payment_creates_wallet_and_pays_driver_share():
    ws = WalletService()
    ws.settle_trip_payment('driver3', 100)
    wallet = ws.get_wallet('driver3')
    assert wallet.balance == 80
