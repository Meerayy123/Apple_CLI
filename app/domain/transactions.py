from datetime import datetime
from enum import Enum

from app.db import db
from sqlalchemy.orm import relationship

class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey("securities.id"), nullable=False)

    tx_type = db.Column(db.Enum(TransactionType), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.String(255), nullable=True)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="transactions")
    portfolio = relationship("Portfolio", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")
