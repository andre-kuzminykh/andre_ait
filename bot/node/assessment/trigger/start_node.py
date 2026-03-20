"""
StartNode — обработка /start и начальных callback-ов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001
"""

import logging

from aiogram.exceptions import TelegramBadRequest

from service.api.assessment_api import AssessmentAPI
from data.messages import welcome_text, question_text
from data.keyboards import start_keyboard, question_keyboard
from state.assessment_state import current_assessment, analysis_messages

logger = logging.getLogger(__name__)
api = AssessmentAPI()


async def safe_edit(message, text, **kwargs):
    """Edit message, silently ignoring 'message is not modified' errors."""
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise


async def handle_start(message):
    """Handle /start command."""
    tg_user = message.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    user_id = user["id"]
    active = await api.get_active_assessment(user_id)
    has_progress = active is not None and active["current_question_index"] > 0

    await message.answer(
        welcome_text(),
        reply_markup=start_keyboard(has_progress),
        parse_mode="HTML",
    )


async def handle_start_assessment(callback):
    """Handle 'start_assessment' callback."""
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    user_id = user["id"]
    assessment = await api.create_assessment(user_id)
    current_assessment[tg_user.id] = assessment["id"]

    await safe_edit(
        callback.message,
        question_text(0),
        reply_markup=question_keyboard(0),
        parse_mode="HTML",
    )
    await callback.answer()


async def handle_continue(callback):
    """Handle 'continue' callback."""
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    user_id = user["id"]
    active = await api.get_active_assessment(user_id)
    if not active:
        await callback.answer("Нет активной диагностики.")
        return

    idx = active["current_question_index"]
    current_assessment[tg_user.id] = active["id"]

    await safe_edit(
        callback.message,
        question_text(idx),
        reply_markup=question_keyboard(idx),
        parse_mode="HTML",
    )
    await callback.answer()
