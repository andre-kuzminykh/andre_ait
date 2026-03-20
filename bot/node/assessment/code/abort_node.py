"""
AbortNode — обработка прерывания и рестарта.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001
"""

import logging

from aiogram.exceptions import TelegramBadRequest

from service.api.assessment_api import AssessmentAPI
from data.messages import (
    welcome_text,
    question_text,
    abort_confirm_text,
    restart_confirm_text,
)
from data.keyboards import (
    start_keyboard,
    question_keyboard,
    abort_confirm_keyboard,
    restart_confirm_keyboard,
)
from state.assessment_state import current_assessment, analysis_messages
from node.assessment.trigger.start_node import safe_edit

from data.assessment.question_bank import QUESTIONS

logger = logging.getLogger(__name__)
api = AssessmentAPI()


async def handle_abort_confirm(callback):
    await safe_edit(
        callback.message,
        abort_confirm_text(),
        reply_markup=abort_confirm_keyboard(),
    )
    await callback.answer()


async def handle_abort_yes(callback):
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    active = await api.get_active_assessment(user["id"])
    answered = active["current_question_index"] if active else 0

    await safe_edit(
        callback.message,
        f"Диагностика приостановлена.\n"
        f"Прогресс сохранен ({answered} из {len(QUESTIONS)} вопросов).\n\n"
        f"Нажмите /start чтобы продолжить.",
    )
    await callback.answer()


async def handle_abort_no(callback):
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    active = await api.get_active_assessment(user["id"])
    if not active:
        await callback.answer("Нет активной диагностики.")
        return
    idx = active["current_question_index"]
    await safe_edit(
        callback.message,
        question_text(idx),
        reply_markup=question_keyboard(idx),
        parse_mode="HTML",
    )
    await callback.answer()


async def handle_restart_confirm(callback):
    await safe_edit(
        callback.message,
        restart_confirm_text(),
        reply_markup=restart_confirm_keyboard(),
    )
    await callback.answer()


async def handle_restart_yes(callback):
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    user_id = user["id"]

    # Delete previous analysis messages
    for msg_id in analysis_messages.pop(tg_user.id, []):
        try:
            await callback.message.chat.delete_message(msg_id)
        except TelegramBadRequest:
            pass

    # Abandon current
    active = await api.get_active_assessment(user_id)
    if active:
        await api.abandon_assessment(active["id"])

    # Create new
    assessment = await api.create_assessment(user_id)
    current_assessment[tg_user.id] = assessment["id"]

    await safe_edit(
        callback.message,
        question_text(0),
        reply_markup=question_keyboard(0),
        parse_mode="HTML",
    )
    await callback.answer()


async def handle_restart_no(callback):
    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    active = await api.get_active_assessment(user["id"])
    if active and active["current_question_index"] > 0:
        idx = active["current_question_index"]
        await safe_edit(
            callback.message,
            question_text(idx),
            reply_markup=question_keyboard(idx),
            parse_mode="HTML",
        )
    else:
        await safe_edit(
            callback.message,
            welcome_text(),
            reply_markup=start_keyboard(
                has_progress=active is not None and active["current_question_index"] > 0
            ),
            parse_mode="HTML",
        )
    await callback.answer()
