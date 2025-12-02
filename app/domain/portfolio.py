from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from app.domain.investment import Investment

@dataclass
class Portfolio:
    id: int
    name: str
    description: str
    holdings: List[Investment] = field(default_factory=list)

    def find_investment(self, ticker: str) -> Optional[Investment]:
        t = ticker.upper()
        for inv in self.holdings:
            if inv.ticker.upper() == t:
                return inv
        return None

    def add_or_update_investment(self, inv: Investment) -> None:
        existing = self.find_investment(inv.ticker)
        if existing:
            existing.quantity += inv.quantity
            # keep purchase price of the last buy for simplicity
            existing.purchase_price = inv.purchase_price
        else:
            self.holdings.append(inv)

    def remove_investment(self, ticker: str) -> None:
        t = ticker.upper()
        self.holdings = [i for i in self.holdings if i.ticker.upper() != t]
