"""Tests for inline keyboards."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.keyboards import question_keyboard, start_keyboard, finish_keyboard


def test_question_keyboard_buttons_one_per_row():
    """Answer buttons should be displayed one per row (vertically stacked)."""
    kb = question_keyboard(0)
    rows = kb.inline_keyboard

    for i in range(5):
        assert len(rows[i]) == 1, f"Row {i} has {len(rows[i])} buttons, expected 1"
        assert rows[i][0].callback_data.startswith("ans:0:")


def test_question_keyboard_has_dont_know():
    """Keyboard should have a 'Don't know' button."""
    kb = question_keyboard(0)
    rows = kb.inline_keyboard
    dont_know_row = rows[5]
    assert len(dont_know_row) == 1
    assert "Не знаю" in dont_know_row[0].text
    assert dont_know_row[0].callback_data == "ans:0:0"


def test_question_keyboard_has_navigation():
    """Keyboard should have navigation buttons."""
    # First question — no back button
    kb0 = question_keyboard(0)
    nav_row = kb0.inline_keyboard[-1]
    assert any("Прервать" in btn.text for btn in nav_row)
    assert not any("Назад" in btn.text for btn in nav_row)

    # Second question — has back button
    kb1 = question_keyboard(1)
    nav_row = kb1.inline_keyboard[-1]
    assert any("Назад" in btn.text for btn in nav_row)
    assert any("Прервать" in btn.text for btn in nav_row)


def test_question_keyboard_answer_values():
    """Answer buttons should have correct callback values 1-5."""
    kb = question_keyboard(0)
    for i in range(5):
        btn = kb.inline_keyboard[i][0]
        assert btn.callback_data == f"ans:0:{i + 1}"


def test_start_keyboard_no_progress():
    kb = start_keyboard(has_progress=False)
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].callback_data == "start_assessment"


def test_start_keyboard_with_progress():
    kb = start_keyboard(has_progress=True)
    assert len(kb.inline_keyboard) == 2


def test_finish_keyboard():
    kb = finish_keyboard()
    assert len(kb.inline_keyboard) == 1
    assert kb.inline_keyboard[0][0].callback_data == "restart_confirm"
