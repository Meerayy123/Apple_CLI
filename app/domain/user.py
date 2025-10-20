from __future__ import annotations
from dataclasses import dataclass

@dataclass
class User:
    first_name: str
    last_name: str
    username: str
    password: str
    balance: float
    is_admin: bool = False
