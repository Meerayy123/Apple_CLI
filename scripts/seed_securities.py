from sqlalchemy import select
from app import create_app
from app.config import Config
from app.db import db
from app.domain.security import Security

app = create_app(Config)

SEED = [
    {"symbol": "AAPL",  "name": "Apple Inc",                 "type": "stock", "price": 195.00},
    {"symbol": "MSFT",  "name": "Microsoft Corp",            "type": "stock", "price": 420.00},
    {"symbol": "GOOGL", "name": "Alphabet Inc (Class A)",    "type": "stock", "price": 175.00},
    {"symbol": "TSLA",  "name": "Tesla Inc",                 "type": "stock", "price": 250.00},
]

with app.app_context():
    for row in SEED:
        existing = db.session.execute(
            select(Security).where(Security.symbol == row["symbol"])
        ).scalar_one_or_none()

        if existing:
            # update if already exists
            existing.name = row["name"]
            existing.type = row["type"]
            existing.price = row["price"]
        else:
            db.session.add(Security(**row))

    db.session.commit()
    print("Seeded securities:", [s["symbol"] for s in SEED])
