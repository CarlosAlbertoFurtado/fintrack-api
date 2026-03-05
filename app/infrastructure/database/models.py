from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Index, Integer, String, Text, func,
)
from sqlalchemy.orm import relationship

from app.infrastructure.database.connection import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(Enum("ADMIN", "USER", name="user_role"), default="USER", nullable=False)
    google_id = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    transactions = relationship("TransactionModel", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("CategoryModel", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("BudgetModel", back_populates="user", cascade="all, delete-orphan")


class CategoryModel(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum("INCOME", "EXPENSE", name="category_type"), nullable=False)
    icon = Column(String(10), nullable=True)
    color = Column(String(7), default="#6366F1", nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="categories")
    transactions = relationship("TransactionModel", back_populates="category")
    budgets = relationship("BudgetModel", back_populates="category")

    __table_args__ = (Index("ix_categories_user_type", "user_id", "type"),)


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum("INCOME", "EXPENSE", name="transaction_type"), nullable=False)
    date = Column(DateTime, default=func.now(), nullable=False)
    notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurring_day = Column(Integer, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="transactions")
    category = relationship("CategoryModel", back_populates="transactions")

    __table_args__ = (
        Index("ix_transactions_user_date", "user_id", "date"),
        Index("ix_transactions_user_type", "user_id", "type"),
        Index("ix_transactions_user_category", "user_id", "category_id"),
    )


class BudgetModel(Base):
    __tablename__ = "budgets"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    spent = Column(Float, default=0.0, nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    alert_threshold = Column(Float, default=0.8, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("UserModel", back_populates="budgets")
    category = relationship("CategoryModel", back_populates="budgets")

    __table_args__ = (Index("ix_budgets_user_month", "user_id", "month", "year"),)
