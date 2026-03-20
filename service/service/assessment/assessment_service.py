"""
AssessmentService — оркестратор бизнес-логики ассессмента.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001, SC002, SC003, SC004, SC005

## Зависимости
- UserRepository, AssessmentRepository, AnswerRepository
- ScoringService, LLMService, ReportService
"""

import json
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundError
from model.enums import AssessmentStatus
from repository.assessment.user_repository import UserRepository
from repository.assessment.assessment_repository import AssessmentRepository
from repository.assessment.answer_repository import AnswerRepository
from service.assessment.scoring_service import ScoringService
from service.assessment.llm_service import LLMService
from service.assessment.report_service import ReportService


class AssessmentService:
    def __init__(self):
        self._user_repo = UserRepository()
        self._assessment_repo = AssessmentRepository()
        self._answer_repo = AnswerRepository()
        self._scoring = ScoringService()
        self._llm = LLMService()
        self._report = ReportService()

    async def get_or_create_user(
        self,
        session: AsyncSession,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ):
        return await self._user_repo.get_or_create(
            session, telegram_user_id, username, first_name, last_name
        )

    async def create_assessment(self, session: AsyncSession, user_id: int):
        return await self._assessment_repo.create(session, user_id=user_id)

    async def get_active_assessment(self, session: AsyncSession, user_id: int):
        return await self._assessment_repo.get_active(session, user_id)

    async def update_progress(self, session: AsyncSession, assessment_id: int, question_index: int):
        return await self._assessment_repo.update(
            session, assessment_id, current_question_index=question_index
        )

    async def abandon_assessment(self, session: AsyncSession, assessment_id: int):
        return await self._assessment_repo.update(
            session, assessment_id, status=AssessmentStatus.ABANDONED.value
        )

    async def save_answer(
        self,
        session: AsyncSession,
        assessment_id: int,
        question_code: str,
        category_code: str,
        option_value: Optional[int],
        score: Optional[int],
        is_unknown: bool,
    ):
        return await self._answer_repo.upsert_answer(
            session, assessment_id, question_code, category_code,
            option_value, score, is_unknown
        )

    async def delete_answer(self, session: AsyncSession, assessment_id: int, question_code: str):
        await self._answer_repo.delete_by_question(session, assessment_id, question_code)

    async def get_answers(self, session: AsyncSession, assessment_id: int) -> List[dict]:
        answers = await self._answer_repo.get_by_assessment(session, assessment_id)
        return [
            {
                "question_code": a.question_code,
                "category_code": a.category_code,
                "option_value": a.option_value,
                "score": a.score,
                "is_unknown": a.is_unknown,
            }
            for a in answers
        ]

    async def complete_assessment(self, session: AsyncSession, assessment_id: int) -> dict:
        answers = await self.get_answers(session, assessment_id)
        result = self._scoring.calculate_results(answers)

        await self._assessment_repo.update(
            session,
            assessment_id,
            status=AssessmentStatus.COMPLETED.value,
            completed_at=datetime.now(timezone.utc),
            total_score_percent=result["total_percent"],
            maturity_level=result["maturity_level"],
            reliability_level=result["reliability"],
            result_json=json.dumps(result, ensure_ascii=False),
        )
        return result

    async def generate_analysis(
        self, session: AsyncSession, assessment_id: int, result: dict
    ) -> dict:
        answers = await self.get_answers(session, assessment_id)
        analysis = await self._llm.generate_analysis(result, answers)

        if not analysis:
            analysis = self._llm.get_fallback_analysis(result["maturity_level"])

        await self._assessment_repo.update(session, assessment_id, llm_analysis=analysis)

        report_html = self._report.generate_html_report(result, analysis)
        report_id = self._report.save_report(report_html)
        report_url = self._report.get_report_url(report_id)

        return {"analysis": analysis, "report_url": report_url}

    def get_report_html(self, report_id: str) -> Optional[str]:
        return self._report.read_report(report_id)
