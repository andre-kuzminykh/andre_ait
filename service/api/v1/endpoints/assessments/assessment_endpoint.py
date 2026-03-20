"""
API v1 endpoints для ассессмента.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001-SC006
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import db_connect
from schema.assessment.user_schema import UserCreateSchema, UserResponseSchema
from schema.assessment.assessment_schema import (
    AssessmentCreateSchema,
    AssessmentResponseSchema,
    AssessmentResultSchema,
    AnalysisResponseSchema,
)
from schema.assessment.answer_schema import AnswerCreateSchema, AnswerResponseSchema
from service.assessment.assessment_service import AssessmentService

router = APIRouter(prefix="/assessments", tags=["assessments"])
service = AssessmentService()


async def get_session():
    async for s in db_connect.get_session():
        yield s


@router.post("/users", response_model=UserResponseSchema)
async def get_or_create_user(
    body: UserCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    user = await service.get_or_create_user(
        session,
        body.telegram_user_id,
        body.username,
        body.first_name,
        body.last_name,
    )
    return user


@router.post("", response_model=AssessmentResponseSchema)
async def create_assessment(
    body: AssessmentCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    assessment = await service.create_assessment(session, body.user_id)
    return assessment


@router.get("/active/{user_id}", response_model=Optional[AssessmentResponseSchema])
async def get_active_assessment(
    user_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_active_assessment(session, user_id)


@router.patch("/{assessment_id}/progress")
async def update_progress(
    assessment_id: int,
    question_index: int,
    session: AsyncSession = Depends(get_session),
):
    await service.update_progress(session, assessment_id, question_index)
    return {"ok": True}


@router.post("/{assessment_id}/abandon")
async def abandon_assessment(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    await service.abandon_assessment(session, assessment_id)
    return {"ok": True}


@router.post("/{assessment_id}/answers", response_model=AnswerResponseSchema)
async def save_answer(
    assessment_id: int,
    body: AnswerCreateSchema,
    session: AsyncSession = Depends(get_session),
):
    answer = await service.save_answer(
        session,
        assessment_id,
        body.question_code,
        body.category_code,
        body.option_value,
        body.score,
        body.is_unknown,
    )
    return answer


@router.delete("/{assessment_id}/answers/{question_code}")
async def delete_answer(
    assessment_id: int,
    question_code: str,
    session: AsyncSession = Depends(get_session),
):
    await service.delete_answer(session, assessment_id, question_code)
    return {"ok": True}


@router.get("/{assessment_id}/answers")
async def get_answers(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_answers(session, assessment_id)


@router.post("/{assessment_id}/complete", response_model=AssessmentResultSchema)
async def complete_assessment(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    return await service.complete_assessment(session, assessment_id)


@router.post("/{assessment_id}/analysis", response_model=AnalysisResponseSchema)
async def generate_analysis(
    assessment_id: int,
    session: AsyncSession = Depends(get_session),
):
    # First get the result from DB
    from repository.assessment.assessment_repository import AssessmentRepository
    import json

    repo = AssessmentRepository()
    assessment = await repo.get_by_id(session, assessment_id)
    if not assessment or not assessment.result_json:
        raise HTTPException(status_code=400, detail="Assessment not completed yet")
    result = json.loads(assessment.result_json)
    return await service.generate_analysis(session, assessment_id, result)
