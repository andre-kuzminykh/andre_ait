"""
AnswerRepository — репозиторий ответов на вопросы.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC002, SC003
"""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from model.assessment.answer_model import AnswerModel
from repository.base_repository import BaseRepository


class AnswerRepository(BaseRepository[AnswerModel]):
    def __init__(self):
        super().__init__(AnswerModel)

    async def get_by_assessment(self, session: AsyncSession, assessment_id: int) -> list[AnswerModel]:
        result = await session.execute(
            select(self.model)
            .where(self.model.assessment_id == assessment_id)
            .order_by(self.model.id)
        )
        return list(result.scalars().all())

    async def upsert_answer(
        self,
        session: AsyncSession,
        assessment_id: int,
        question_code: str,
        category_code: str,
        option_value: int | None,
        score: int | None,
        is_unknown: bool,
    ) -> AnswerModel:
        result = await session.execute(
            select(self.model).where(
                self.model.assessment_id == assessment_id,
                self.model.question_code == question_code,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.option_value = option_value
            existing.score = score
            existing.is_unknown = is_unknown
            existing.category_code = category_code
            await session.commit()
            await session.refresh(existing)
            return existing
        return await self.create(
            session,
            assessment_id=assessment_id,
            question_code=question_code,
            category_code=category_code,
            option_value=option_value,
            score=score,
            is_unknown=is_unknown,
        )

    async def delete_by_question(
        self, session: AsyncSession, assessment_id: int, question_code: str
    ) -> None:
        await session.execute(
            delete(self.model).where(
                self.model.assessment_id == assessment_id,
                self.model.question_code == question_code,
            )
        )
        await session.commit()

    async def delete_all_for_assessment(self, session: AsyncSession, assessment_id: int) -> None:
        await session.execute(
            delete(self.model).where(self.model.assessment_id == assessment_id)
        )
        await session.commit()
