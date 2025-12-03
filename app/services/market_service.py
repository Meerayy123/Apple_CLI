from __future__ import annotations
from typing import List
import db
from app.domain.security import Security

def list_market_securities() -> List[Security]:
    return db.list_securities()
