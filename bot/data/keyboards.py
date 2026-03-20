"""
Inline keyboards for the bot.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001-SC005
"""

import importlib.util
import os

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Load question_bank from service/data/assessment/ without polluting sys.path
_qb_path = os.path.join(
    os.path.dirname(__file__), "..", "..", "service", "data", "assessment", "question_bank.py"
)
_spec = importlib.util.spec_from_file_location("_question_bank_kb", _qb_path)
_qb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_qb)

QUESTIONS = _qb.QUESTIONS


def start_keyboard(has_progress: bool = False) -> InlineKeyboardMarkup:
    if has_progress:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Продолжить", callback_data="continue")],
            [InlineKeyboardButton(text="🔄 Начать заново", callback_data="restart_confirm")],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать диагностику", callback_data="start_assessment")],
    ])


def question_keyboard(question_index: int) -> InlineKeyboardMarkup:
    """Build keyboard for a question: 5 answer buttons + Don't know + Back + Abort."""
    q = QUESTIONS[question_index]
    buttons = []

    for i, btn_text in enumerate(q["buttons"]):
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"ans:{question_index}:{i + 1}",
        )])

    buttons.append([
        InlineKeyboardButton(text="🤷 Не знаю", callback_data=f"ans:{question_index}:0"),
    ])

    nav_row = []
    if question_index > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"back:{question_index}"))
    nav_row.append(InlineKeyboardButton(text="⏹ Прервать", callback_data="abort_confirm"))
    buttons.append(nav_row)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def abort_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, выйти", callback_data="abort_yes"),
            InlineKeyboardButton(text="Продолжить", callback_data="abort_no"),
        ],
    ])


def restart_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да, начать заново", callback_data="restart_yes"),
            InlineKeyboardButton(text="Отмена", callback_data="restart_no"),
        ],
    ])


def finish_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Пройти заново", callback_data="restart_confirm")],
    ])


def report_keyboard(report_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📎 Развернутые рекомендации", url=report_url)],
    ])
