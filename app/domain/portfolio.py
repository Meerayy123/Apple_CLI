from app.db import db
from sqlalchemy.orm import relationship

class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="portfolios")
    investments = relationship("Investment", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio", cascade="all, delete-orphan")
