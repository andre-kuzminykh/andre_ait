"""
Assessment handler — aiogram Router wiring.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC001-SC005

Routes all callback queries and commands to the appropriate nodes.
"""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from node.assessment.trigger.start_node import (
    handle_start,
    handle_start_assessment,
    handle_continue,
)
from node.assessment.code.abort_node import (
    handle_abort_confirm,
    handle_abort_yes,
    handle_abort_no,
    handle_restart_confirm,
    handle_restart_yes,
    handle_restart_no,
)
from node.assessment.answer.answer_node import (
    handle_answer,
    handle_back,
)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await handle_start(message)


@router.callback_query(F.data == "start_assessment")
async def on_start_assessment(callback: CallbackQuery):
    await handle_start_assessment(callback)


@router.callback_query(F.data == "continue")
async def on_continue(callback: CallbackQuery):
    await handle_continue(callback)


@router.callback_query(F.data.startswith("ans:"))
async def on_answer(callback: CallbackQuery):
    await handle_answer(callback)


@router.callback_query(F.data.startswith("back:"))
async def on_back(callback: CallbackQuery):
    await handle_back(callback)


@router.callback_query(F.data == "abort_confirm")
async def on_abort_confirm(callback: CallbackQuery):
    await handle_abort_confirm(callback)


@router.callback_query(F.data == "abort_yes")
async def on_abort_yes(callback: CallbackQuery):
    await handle_abort_yes(callback)


@router.callback_query(F.data == "abort_no")
async def on_abort_no(callback: CallbackQuery):
    await handle_abort_no(callback)


@router.callback_query(F.data == "restart_confirm")
async def on_restart_confirm(callback: CallbackQuery):
    await handle_restart_confirm(callback)


@router.callback_query(F.data == "restart_yes")
async def on_restart_yes(callback: CallbackQuery):
    await handle_restart_yes(callback)


@router.callback_query(F.data == "restart_no")
async def on_restart_no(callback: CallbackQuery):
    await handle_restart_no(callback)
