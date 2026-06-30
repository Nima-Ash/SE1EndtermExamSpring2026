from dataclasses import dataclass, field
from typing import Dict
DRIVER_COMMISSION_RATE = 0.8

@dataclass
class Wallet:
    owner_id: str
    balance: float = 0.0
    currency: str = 'USDT'

class WalletService:

    def __init__(self) -> None:
        self._wallets: Dict[str, Wallet] = {}

    def create_wallet(self, owner_id: str, currency: str='USDT') -> Wallet:
        if owner_id in self._wallets:
            raise ValueError('wallet already exists')
        wallet = Wallet(owner_id=owner_id, currency=currency)
        self._wallets[owner_id] = wallet
        return wallet

    def get_wallet(self, owner_id: str) -> Wallet:
        wallet = self._wallets.get(owner_id)
        if wallet is None:
            raise ValueError('wallet not found')
        return wallet

    def deposit(self, owner_id: str, amount: float) -> Wallet:
        if amount <= 0:
            raise ValueError('amount must be positive')
        wallet = self.get_wallet(owner_id)
        wallet.balance = round(wallet.balance + amount, 8)
        return wallet

    def withdraw(self, owner_id: str, amount: float) -> Wallet:
        wallet = self.get_wallet(owner_id)
        if amount <= 0:
            raise ValueError('amount must be positive')
        if wallet.balance < amount:
            raise ValueError('insufficient balance')
        wallet.balance = round(wallet.balance - amount, 8)
        return wallet

    def settle_trip_payment(self, driver_id: str, fare_amount: float) -> Wallet:
        driver_share = round(fare_amount * DRIVER_COMMISSION_RATE, 8)
        if driver_id not in self._wallets:
            self.create_wallet(driver_id)
        return self.deposit(driver_id, driver_share)
