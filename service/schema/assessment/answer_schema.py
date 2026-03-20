"""
Pydantic-схемы ответов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC002
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnswerCreateSchema(BaseModel):
    question_code: str
    category_code: str
    option_value: Optional[int] = None
    score: Optional[int] = None
    is_unknown: bool = False


class AnswerResponseSchema(BaseModel):
    id: int
    assessment_id: int
    question_code: str
    category_code: str
    option_value: Optional[int]
    score: Optional[int]
    is_unknown: bool
    created_at: datetime

    class Config:
        from_attributes = True
