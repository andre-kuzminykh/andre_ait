"""Tests for bot message templates."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from data.messages import (
    welcome_text,
    question_text,
    abort_confirm_text,
    restart_confirm_text,
    result_text,
    progress_text,
)


def test_welcome_text_content():
    text = welcome_text()
    assert "Диагностика AI-зрелости" in text
    assert "35 вопросов" in text
    assert "7 категорий" in text


def test_question_text_first():
    text = question_text(0)
    assert "Вопрос 1 из 35" in text
    assert "Категория 1" in text
    assert "<b>" in text  # HTML formatting


def test_question_text_last():
    text = question_text(34)
    assert "Вопрос 35 из 35" in text


def test_question_text_middle():
    text = question_text(10)
    assert "Вопрос 11 из 35" in text


def test_abort_confirm_text():
    text = abort_confirm_text()
    assert "Остановить" in text
    assert "сохранится" in text


def test_restart_confirm_text():
    text = restart_confirm_text()
    assert "заново" in text


def test_result_text():
    result = {
        "total_percent": 50.0,
        "maturity_level": "AI-Driven",
        "reliability": "Высокая",
        "categories": [
            {"emoji": "🎯", "name": "Стратегия", "percent": 50.0, "tentative": False},
        ],
    }
    text = result_text(result)
    assert "50.0%" in text
    assert "AI-Driven" in text
    assert "Стратегия" in text


def test_result_text_tentative():
    result = {
        "total_percent": 30.0,
        "maturity_level": "AI-Enabled",
        "reliability": "Средняя",
        "categories": [
            {"emoji": "🎯", "name": "Стратегия", "percent": 30.0, "tentative": True},
        ],
    }
    text = result_text(result)
    assert "≈" in text


def test_progress_text():
    text = progress_text(10, 35)
    assert "10" in text
    assert "35" in text
