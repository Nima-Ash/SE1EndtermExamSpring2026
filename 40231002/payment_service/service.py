from dataclasses import dataclass
from enum import Enum
from typing import Dict
import hashlib
import time

class PaymentStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'

@dataclass
class CryptoPayment:
    payment_id: str
    trip_id: str
    amount: float
    currency: str
    wallet_address: str
    status: PaymentStatus = PaymentStatus.PENDING
    tx_hash: str = ''

class PaymentService:
    SUPPORTED_CURRENCIES = {'BTC', 'ETH', 'USDT'}

    def __init__(self) -> None:
        self._payments: Dict[str, CryptoPayment] = {}

    def initiate_payment(self, payment_id: str, trip_id: str, amount: float, currency: str, wallet_address: str) -> CryptoPayment:
        if currency not in self.SUPPORTED_CURRENCIES:
            raise ValueError(f'unsupported currency: {currency}')
        if amount <= 0:
            raise ValueError('amount must be positive')
        payment = CryptoPayment(payment_id=payment_id, trip_id=trip_id, amount=amount, currency=currency, wallet_address=wallet_address)
        self._payments[payment_id] = payment
        return payment

    def confirm_payment(self, payment_id: str) -> CryptoPayment:
        payment = self._get(payment_id)
        raw = f'{payment.payment_id}{payment.trip_id}{payment.amount}{time.time()}'
        payment.tx_hash = hashlib.sha256(raw.encode()).hexdigest()
        payment.status = PaymentStatus.CONFIRMED
        return payment

    def fail_payment(self, payment_id: str, reason: str='') -> CryptoPayment:
        payment = self._get(payment_id)
        payment.status = PaymentStatus.FAILED
        return payment

    def _get(self, payment_id: str) -> CryptoPayment:
        payment = self._payments.get(payment_id)
        if payment is None:
            raise ValueError('payment not found')
        return payment
