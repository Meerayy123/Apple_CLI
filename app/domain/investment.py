from app.db import db
from sqlalchemy.orm import relationship

class Investment(db.Model):
    __tablename__ = "investments"

    id = db.Column(db.Integer, primary_key=True, index=True)

    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=False)
    security_id = db.Column(db.Integer, db.ForeignKey("securities.id"), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)

    portfolio = relationship("Portfolio", back_populates="investments")
    security = relationship("Security", back_populates="investments")
