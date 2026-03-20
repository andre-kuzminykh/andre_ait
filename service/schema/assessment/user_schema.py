"""
Pydantic-схемы пользователя.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001
"""

from datetime import datetime

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    telegram_user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserResponseSchema(BaseModel):
    id: int
    telegram_user_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True
