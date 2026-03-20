"""
AssessmentModel — модель ассессмента AI-зрелости.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC003, SC004
"""

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime

from model.base_model import Base, BaseModel
from model.enums import AssessmentStatus


class AssessmentModel(Base, BaseModel):
    __tablename__ = "assessments"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, default=AssessmentStatus.IN_PROGRESS.value)
    current_question_index = Column(Integer, nullable=False, default=0)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    total_score_percent = Column(Float, nullable=True)
    maturity_level = Column(String(50), nullable=True)
    reliability_level = Column(String(20), nullable=True)
    result_json = Column(Text, nullable=True)
    llm_analysis = Column(Text, nullable=True)
