"""
QuestionService — сервис банка вопросов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC006

## Зависимости
- data.assessment.question_bank
"""

from data.assessment.question_bank import (
    CATEGORIES,
    QUESTIONS,
    get_category_by_code,
    get_questions_by_category,
)


class QuestionService:
    def get_all_questions(self) -> list[dict]:
        return QUESTIONS

    def get_all_categories(self) -> list[dict]:
        return CATEGORIES

    def get_category(self, code: str) -> dict | None:
        return get_category_by_code(code)

    def get_questions_for_category(self, category_code: str) -> list[dict]:
        return get_questions_by_category(category_code)

    def get_question_by_index(self, index: int) -> dict | None:
        if 0 <= index < len(QUESTIONS):
            return QUESTIONS[index]
        return None

    def total_questions(self) -> int:
        return len(QUESTIONS)
