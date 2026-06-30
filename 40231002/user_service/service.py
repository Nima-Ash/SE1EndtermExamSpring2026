from dataclasses import dataclass, field
from typing import Dict

@dataclass
class User:
    user_id: str
    name: str
    phone: str
    role: str
    is_authenticated: bool = False

class UserService:

    def __init__(self) -> None:
        self._users: Dict[str, User] = {}

    def register(self, user_id: str, name: str, phone: str, role: str) -> User:
        if role not in ('passenger', 'driver'):
            raise ValueError("role must be 'passenger' or 'driver'")
        if user_id in self._users:
            raise ValueError(f'user {user_id} already exists')
        user = User(user_id=user_id, name=name, phone=phone, role=role)
        self._users[user_id] = user
        return user

    def login(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError('user not found')
        user.is_authenticated = True
        return user

    def get_user(self, user_id: str) -> User:
        user = self._users.get(user_id)
        if user is None:
            raise ValueError('user not found')
        return user
