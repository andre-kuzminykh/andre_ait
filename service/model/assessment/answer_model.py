"""
AnswerModel — модель ответа на вопрос диагностики.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC002, SC003
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint

from model.base_model import Base, BaseModel


class AnswerModel(Base, BaseModel):
    __tablename__ = "answers"

    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    question_code = Column(String(20), nullable=False)
    category_code = Column(String(50), nullable=False)
    option_value = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    is_unknown = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint("assessment_id", "question_code", name="uq_assessment_question"),
    )
