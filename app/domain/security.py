from app.db import db
from sqlalchemy.orm import relationship

class Security(db.Model):
    __tablename__ = "securities"

    id = db.Column(db.Integer, primary_key=True, index=True)
    symbol = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)

    investments = relationship("Investment", back_populates="security", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="security", cascade="all, delete-orphan")
