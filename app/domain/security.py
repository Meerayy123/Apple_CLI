from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Security:
    ticker: str
    issuer: str
    price: float
