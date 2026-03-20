"""
API v1 endpoints для банка вопросов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC006
"""

from fastapi import APIRouter

from service.assessment.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["questions"])
question_service = QuestionService()


@router.get("")
async def get_all_questions():
    return question_service.get_all_questions()


@router.get("/categories")
async def get_categories():
    return question_service.get_all_categories()


@router.get("/categories/{category_code}")
async def get_questions_by_category(category_code: str):
    return question_service.get_questions_for_category(category_code)


@router.get("/{index}")
async def get_question_by_index(index: int):
    q = question_service.get_question_by_index(index)
    if q is None:
        return {"error": "Question not found"}
    return q


@router.get("/count/total")
async def get_total_count():
    return {"total": question_service.total_questions()}
