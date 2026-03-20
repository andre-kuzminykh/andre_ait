"""
Pydantic-схемы ассессмента.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC003, SC004
"""

from datetime import datetime
from typing import Dict, List, Optional

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
    completed_at: Optional[datetime]
    total_score_percent: Optional[float]
    maturity_level: Optional[str]
    reliability_level: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentResultSchema(BaseModel):
    total_percent: float
    weighted_avg: float
    maturity_level: str
    reliability: str
    unknown_count: int
    categories: List[Dict]
    strengths: List[Dict]
    weaknesses: List[Dict]


class AnalysisResponseSchema(BaseModel):
    analysis: str
    report_url: Optional[str] = None
