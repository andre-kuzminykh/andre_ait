"""
AnswerNode — обработка ответов на вопросы и показ результатов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC002, SC003, SC004, SC005
"""

import html as html_mod
import logging
import re
from typing import List

from aiogram.enums import ParseMode

from service.api.assessment_api import AssessmentAPI
from data.messages import question_text, result_text
from data.keyboards import question_keyboard, finish_keyboard
from state.assessment_state import analysis_messages
from node.assessment.trigger.start_node import safe_edit

from data.assessment.question_bank import QUESTIONS

logger = logging.getLogger(__name__)
api = AssessmentAPI()


async def handle_answer(callback):
    """Handle answer callback: ans:{q_index}:{value}."""
    parts = callback.data.split(":")
    q_index = int(parts[1])
    value = int(parts[2])  # 0 = don't know, 1-5 = answer

    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    active = await api.get_active_assessment(user["id"])
    if not active:
        await callback.answer("Начните диагностику заново с /start")
        return

    assessment_id = active["id"]
    question = QUESTIONS[q_index]

    is_unknown = value == 0
    score = value if not is_unknown else None

    await api.save_answer(
        assessment_id=assessment_id,
        question_code=question["code"],
        category_code=question["category"],
        option_value=value if not is_unknown else None,
        score=score,
        is_unknown=is_unknown,
    )

    next_index = q_index + 1
    await api.update_progress(assessment_id, next_index)

    # Last question — show results
    if next_index >= len(QUESTIONS):
        await _show_results(callback, assessment_id)
        return

    await safe_edit(
        callback.message,
        question_text(next_index),
        reply_markup=question_keyboard(next_index),
        parse_mode="HTML",
    )
    await callback.answer()


async def handle_back(callback):
    """Handle back button: back:{q_index}."""
    q_index = int(callback.data.split(":")[1])
    prev_index = q_index - 1
    if prev_index < 0:
        await callback.answer()
        return

    tg_user = callback.from_user
    user = await api.get_or_create_user(
        tg_user.id, tg_user.username, tg_user.first_name, tg_user.last_name
    )
    active = await api.get_active_assessment(user["id"])
    if active:
        prev_question = QUESTIONS[prev_index]
        await api.delete_answer(active["id"], prev_question["code"])
        await api.update_progress(active["id"], prev_index)

    await safe_edit(
        callback.message,
        question_text(prev_index),
        reply_markup=question_keyboard(prev_index),
        parse_mode="HTML",
    )
    await callback.answer()


async def _show_results(callback, assessment_id: int):
    """Calculate results, show deterministic part, then call LLM."""
    result = await api.complete_assessment(assessment_id)

    # Send deterministic result
    await safe_edit(
        callback.message,
        result_text(result),
        reply_markup=finish_keyboard(),
        parse_mode="HTML",
    )

    # Call LLM for analysis
    loading_msg = await callback.message.answer("⏳ Генерирую расширенный анализ...")

    analysis_data = await api.generate_analysis(assessment_id)
    await loading_msg.delete()

    analysis = analysis_data.get("analysis")
    report_url = analysis_data.get("report_url")
    report_link_text = f'\n\n📎 Развернутые рекомендации:\n{report_url}' if report_url else ""
    tg_user_id = callback.from_user.id
    sent_ids: List[int] = []

    if analysis:
        formatted = _format_analysis(analysis)
        chunks = _split_message(formatted, 3800)
        for i, chunk in enumerate(chunks):
            is_last = i == len(chunks) - 1
            text = chunk + report_link_text if is_last else chunk
            msg = await callback.message.answer(text, parse_mode=ParseMode.HTML)
            sent_ids.append(msg.message_id)
    else:
        msg = await callback.message.answer(
            "Расширенный анализ временно недоступен." + report_link_text,
            parse_mode=ParseMode.HTML,
        )
        sent_ids.append(msg.message_id)

    analysis_messages[tg_user_id] = sent_ids
    await callback.answer()


def _format_analysis(text: str) -> str:
    """Format LLM analysis with HTML bold headers and spacing."""
    text = html_mod.escape(text)
    text = re.sub(
        r'^((?:📊|📋|💡)[^\n]+)',
        r'\n<b>\1</b>\n',
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r'^((?:🚀|📅|🎯)[^\n:]+:)(.*)',
        r'\n<b>\1</b>\2',
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r'^([SWOT]:)',
        r'<b>\1</b>',
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _split_message(text: str, max_len: int = 4000) -> List[str]:
    """Split text into chunks respecting line breaks."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_len:
            if current:
                chunks.append(current)
            current = line
        else:
            current = current + "\n" + line if current else line
    if current:
        chunks.append(current)
    return chunks
