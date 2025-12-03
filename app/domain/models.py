# app/domain/models.py
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    ForeignKey,
    DateTime,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship

from db import Base


class TransactionKind(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    portfolios = relationship("Portfolio", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    label = Column(String(200), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="portfolios")
    positions = relationship("Investment", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio")


class Security(Base):
    __tablename__ = "securities"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="STOCK")
    last_price = Column(Float, nullable=False)

    positions = relationship("Investment", back_populates="security")
    transactions = relationship("Transaction", back_populates="security")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)

    portfolio = relationship("Portfolio", back_populates="positions")
    security = relationship("Security", back_populates="positions")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)

    kind = Column(SAEnum(TransactionKind), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    security_id = Column(Integer, ForeignKey("securities.id"), nullable=False)

    user = relationship("User", back_populates="transactions")
    portfolio = relationship("Portfolio", back_populates="transactions")
    security = relationship("Security", back_populates="transactions")