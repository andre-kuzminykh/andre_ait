"""
Pydantic-схемы пользователя.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponseSchema(BaseModel):
    id: int
    telegram_user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
