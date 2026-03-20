"""
UserModel — модель пользователя Telegram.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC002, SC003
"""

from sqlalchemy import Column, Integer, String

from model.base_model import Base, BaseModel


class UserModel(Base, BaseModel):
    __tablename__ = "users"

    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
