from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Investment:
    ticker: str
    quantity: int
    purchase_price: float
