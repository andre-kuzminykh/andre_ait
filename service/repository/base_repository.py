"""
Базовый репозиторий с CRUD-операциями.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

from typing import Generic, List, Optional, TypeVar, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, session: AsyncSession, entity_id: int) -> Optional[T]:
        return await session.get(self.model, entity_id)

    async def get_all(self, session: AsyncSession) -> List[T]:
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(self, session: AsyncSession, **kwargs) -> T:
        instance = self.model(**kwargs)
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def update(self, session: AsyncSession, entity_id: int, **kwargs) -> Optional[T]:
        instance = await self.get_by_id(session, entity_id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, entity_id: int) -> bool:
        instance = await self.get_by_id(session, entity_id)
        if not instance:
            return False
        await session.delete(instance)
        await session.commit()
        return True
