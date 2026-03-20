"""
API-клиент для взаимодействия бота с бэкенд-сервисом.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001-SC006

## Бизнес-контекст
Бот не обращается к БД напрямую — все операции идут через REST API.
"""

import logging
from typing import Dict, List, Optional

import httpx

from core.config import config

logger = logging.getLogger(__name__)


class AssessmentAPI:
    def __init__(self):
        self._base = config.api_url

    def _url(self, path: str) -> str:
        return f"{self._base}{path}"

    async def get_or_create_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._url("/assessments/users"),
                json={
                    "telegram_user_id": telegram_user_id,
                    "username": username,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )
            r.raise_for_status()
            return r.json()

    async def create_assessment(self, user_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._url("/assessments"),
                json={"user_id": user_id},
            )
            r.raise_for_status()
            return r.json()

    async def get_active_assessment(self, user_id: int) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._url(f"/assessments/active/{user_id}"))
            r.raise_for_status()
            data = r.json()
            return data if data else None

    async def update_progress(self, assessment_id: int, question_index: int):
        async with httpx.AsyncClient() as client:
            r = await client.patch(
                self._url(f"/assessments/{assessment_id}/progress"),
                params={"question_index": question_index},
            )
            r.raise_for_status()

    async def abandon_assessment(self, assessment_id: int):
        async with httpx.AsyncClient() as client:
            r = await client.post(self._url(f"/assessments/{assessment_id}/abandon"))
            r.raise_for_status()

    async def save_answer(
        self,
        assessment_id: int,
        question_code: str,
        category_code: str,
        option_value: Optional[int],
        score: Optional[int],
        is_unknown: bool,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._url(f"/assessments/{assessment_id}/answers"),
                json={
                    "question_code": question_code,
                    "category_code": category_code,
                    "option_value": option_value,
                    "score": score,
                    "is_unknown": is_unknown,
                },
            )
            r.raise_for_status()
            return r.json()

    async def delete_answer(self, assessment_id: int, question_code: str):
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                self._url(f"/assessments/{assessment_id}/answers/{question_code}")
            )
            r.raise_for_status()

    async def get_answers(self, assessment_id: int) -> List[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._url(f"/assessments/{assessment_id}/answers"))
            r.raise_for_status()
            return r.json()

    async def complete_assessment(self, assessment_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._url(f"/assessments/{assessment_id}/complete"),
                timeout=30.0,
            )
            r.raise_for_status()
            return r.json()

    async def generate_analysis(self, assessment_id: int) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                self._url(f"/assessments/{assessment_id}/analysis"),
                timeout=60.0,
            )
            r.raise_for_status()
            return r.json()

    async def get_questions(self) -> List[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._url("/questions"))
            r.raise_for_status()
            return r.json()

    async def get_question_by_index(self, index: int) -> Optional[dict]:
        async with httpx.AsyncClient() as client:
            r = await client.get(self._url(f"/questions/{index}"))
            r.raise_for_status()
            data = r.json()
            return data if "error" not in data else None
