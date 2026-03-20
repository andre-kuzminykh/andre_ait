"""
Pydantic-схемы ответов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC002
"""

from datetime import datetime

from pydantic import BaseModel


class AnswerCreateSchema(BaseModel):
    question_code: str
    category_code: str
    option_value: int | None = None
    score: int | None = None
    is_unknown: bool = False


class AnswerResponseSchema(BaseModel):
    id: int
    assessment_id: int
    question_code: str
    category_code: str
    option_value: int | None
    score: int | None
    is_unknown: bool
    created_at: datetime

    class Config:
        from_attributes = True
