"""
AssessmentRepository — репозиторий ассессментов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC003, SC004
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.assessment.assessment_model import AssessmentModel
from model.enums import AssessmentStatus
from repository.base_repository import BaseRepository


class AssessmentRepository(BaseRepository[AssessmentModel]):
    def __init__(self):
        super().__init__(AssessmentModel)

    async def get_active(self, session: AsyncSession, user_id: int) -> Optional[AssessmentModel]:
        result = await session.execute(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.status == AssessmentStatus.IN_PROGRESS.value,
            )
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_last_completed(self, session: AsyncSession, user_id: int) -> Optional[AssessmentModel]:
        result = await session.execute(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.status == AssessmentStatus.COMPLETED.value,
            )
            .order_by(self.model.completed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
