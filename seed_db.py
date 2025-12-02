# seed_db.py

from db import get_session
from app.domain.models import User, Security


def seed() -> None:
    print("Seeding database...")

    with get_session() as session:
        # --- Demo admin user ---
        demo_email = "demo@applecli.local"
        user = session.query(User).filter_by(email=demo_email).first()
        if not user:
            user = User(
                name="Demo User",
                email=demo_email,
                is_admin=True,
            )
            session.add(user)
            print(f"  Created user: {user.email}")
        else:
            print(f"  User already exists: {user.email}")

        # --- Some default securities ---
        defaults = [
            ("AAPL", "Apple Inc.", "STOCK", 190.0),
            ("MSFT", "Microsoft Corp.", "STOCK", 380.0),
            ("TSLA", "Tesla Inc.", "STOCK", 220.0),
        ]

        for symbol, name, category, price in defaults:
            sec = session.query(Security).filter_by(symbol=symbol).first()
            if not sec:
                sec = Security(
                    symbol=symbol,
                    name=name,
                    category=category,
                    last_price=price,
                )
                session.add(sec)
                print(f"  Created security: {symbol}")
            else:
                print(f"  Security already exists: {symbol}")

    print("Seeding completed.")
    

if __name__ == "__main__":
    seed()
