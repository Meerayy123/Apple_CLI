# init_db.py

from db import Base, engine
import app.domain.models  # noqa: F401  # register models

def init_db() -> None:
    print("Creating tables...")
    print("Mapped tables before create_all:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    print("Mapped tables after create_all:", list(Base.metadata.tables.keys()))
    print("Tables created successfully.")

if __name__ == "__main__":
    init_db()