from __future__ import annotations
import db
from app.domain.security import Security
from typing import List

def list_market_securities() -> List[Security]:
    return db.list_securities()
