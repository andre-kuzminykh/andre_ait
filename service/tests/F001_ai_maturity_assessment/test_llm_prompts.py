"""Tests for LLM prompt generation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from service.assessment.llm_service import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, LLMService
from service.assessment.scoring_service import ScoringService
from data.assessment.question_bank import QUESTIONS

scoring = ScoringService()
llm = LLMService()


def _make_answer(question_code, category_code, score, is_unknown=False):
    return {
        "question_code": question_code,
        "category_code": category_code,
        "score": score,
        "is_unknown": is_unknown,
        "option_value": score,
    }


def test_system_prompt_exists():
    assert len(SYSTEM_PROMPT) > 50
    assert "русском" in SYSTEM_PROMPT


def test_system_prompt_contains_maturity_levels():
    assert "Начальный" in SYSTEM_PROMPT
    assert "AI-Enabled" in SYSTEM_PROMPT
    assert "AI-Driven" in SYSTEM_PROMPT
    assert "AI-First" in SYSTEM_PROMPT
    assert "AI-Native" in SYSTEM_PROMPT


def test_system_prompt_enforces_brevity():
    assert "2000" in SYSTEM_PROMPT


def test_system_prompt_forbids_extra_sections():
    """System prompt must explicitly forbid AS-IS and other verbose sections."""
    assert "ЗАПРЕЩЕНО" in SYSTEM_PROMPT
    assert "AS-IS" in SYSTEM_PROMPT
    assert "РОВНО 3 раздела" in SYSTEM_PROMPT


def test_user_prompt_has_exactly_three_sections():
    """User prompt should request exactly 3 sections."""
    assert "Интерпретация" in USER_PROMPT_TEMPLATE
    assert "SWOT" in USER_PROMPT_TEMPLATE
    assert "Рекомендации" in USER_PROMPT_TEMPLATE
    assert "РОВНО 3 раздела" in USER_PROMPT_TEMPLATE


def test_prompt_interpretation_no_bullets():
    assert "Сплошной текст" in USER_PROMPT_TEMPLATE
    assert "Без буллетов" in USER_PROMPT_TEMPLATE


def test_prompt_swot_no_bullets():
    """SWOT should use S:/W:/O:/T: format without sub-bullets."""
    assert "S: текст без буллетов" in USER_PROMPT_TEMPLATE
    assert "W: текст без буллетов" in USER_PROMPT_TEMPLATE


def test_prompt_has_roadmap_recommendations():
    assert "Быстрые шаги" in USER_PROMPT_TEMPLATE
    assert "Среднесрочные" in USER_PROMPT_TEMPLATE
    assert "Долгосрочные" in USER_PROMPT_TEMPLATE


def test_prompt_quick_steps_start_with_strategy():
    assert "стратегии" in USER_PROMPT_TEMPLATE.lower()


def test_no_asis_in_user_prompt():
    """User prompt must NOT contain verbose sections."""
    assert "AS-IS" not in USER_PROMPT_TEMPLATE
    assert "Процессные шаги" not in USER_PROMPT_TEMPLATE
    assert "Узкие места" not in USER_PROMPT_TEMPLATE
    assert "Потенциал автоматизации" not in USER_PROMPT_TEMPLATE


def test_build_user_prompt():
    answers = [_make_answer(q["code"], q["category"], 3) for q in QUESTIONS]
    result = scoring.calculate_results(answers)
    prompt = llm.build_user_prompt(result, answers, {q["code"]: q for q in QUESTIONS})
    assert "50.0%" in prompt
    assert "AI-Driven" in prompt
    assert len(prompt) > 200


def test_build_user_prompt_low_score():
    answers = [_make_answer(q["code"], q["category"], 1) for q in QUESTIONS]
    result = scoring.calculate_results(answers)
    prompt = llm.build_user_prompt(result, answers, {q["code"]: q for q in QUESTIONS})
    assert "Начальный" in prompt
    assert "0.0%" in prompt


def test_prompt_with_unknown_answers():
    answers = []
    for i, q in enumerate(QUESTIONS):
        if i < 5:
            answers.append(_make_answer(q["code"], q["category"], None, is_unknown=True))
        else:
            answers.append(_make_answer(q["code"], q["category"], 4))
    result = scoring.calculate_results(answers)
    prompt = llm.build_user_prompt(result, answers, {q["code"]: q for q in QUESTIONS})
    assert "Не знаю" in prompt
