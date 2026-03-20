"""
Pydantic-схемы ассессмента.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC003, SC004
"""

from datetime import datetime

from pydantic import BaseModel


class AssessmentCreateSchema(BaseModel):
    user_id: int


class AssessmentUpdateProgressSchema(BaseModel):
    current_question_index: int


class AssessmentCompleteSchema(BaseModel):
    total_score_percent: float
    maturity_level: str
    reliability_level: str
    result_json: str


class AssessmentResponseSchema(BaseModel):
    id: int
    user_id: int
    status: str
    current_question_index: int
    completed_at: datetime | None
    total_score_percent: float | None
    maturity_level: str | None
    reliability_level: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentResultSchema(BaseModel):
    total_percent: float
    weighted_avg: float
    maturity_level: str
    reliability: str
    unknown_count: int
    categories: list[dict]
    strengths: list[dict]
    weaknesses: list[dict]


class AnalysisResponseSchema(BaseModel):
    analysis: str
    report_url: str | None = None
