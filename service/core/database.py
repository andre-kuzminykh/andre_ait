"""
Подключение к БД: AsyncSession, engine.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import config


class DatabaseConnect:
    def __init__(self):
        self.engine = create_async_engine(config.database_url, echo=False)
        self.session_maker = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self):
        async with self.session_maker() as session:
            yield session


db_connect = DatabaseConnect()
