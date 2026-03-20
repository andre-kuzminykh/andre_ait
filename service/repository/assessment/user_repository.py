"""
UserRepository — репозиторий пользователей.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from model.assessment.user_model import UserModel
from repository.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)

    async def get_or_create(
        self,
        session: AsyncSession,
        telegram_user_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> UserModel:
        result = await session.execute(
            select(self.model).where(self.model.telegram_user_id == telegram_user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            return user
        return await self.create(
            session,
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
