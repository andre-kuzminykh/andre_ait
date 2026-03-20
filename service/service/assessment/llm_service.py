"""
LLMService — генерация анализа через OpenAI-совместимый API.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC004

## Бизнес-контекст
Генерирует расширенный анализ: интерпретация, SWOT, рекомендации.
При недоступности LLM — fallback по уровню зрелости.

## Зависимости
- core.config
- data.assessment.question_bank
"""

import logging
from typing import Dict, List, Optional

from openai import AsyncOpenAI

from core.config import config
from data.assessment.question_bank import QUESTIONS

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """Ты — эксперт по цифровой трансформации и внедрению ИИ в компаниях.
Тебе дают результаты диагностики AI-зрелости компании.
Твоя задача — дать краткий, конкретный и полезный анализ.

Правила:
- Пиши на русском языке.
- Будь максимально кратким — весь ответ СТРОГО до 2000 символов.
- Не повторяй числовые результаты — они уже показаны пользователю.
- Не придумывай факты о компании.
- Не используй маркетинговый язык и воду.
- Давай практичные, применимые советы.
- Формат ответа — текст с эмодзи-заголовками, без markdown-разметки.
- ЗАПРЕЩЕНО добавлять разделы, которых нет в шаблоне. Никаких AS-IS, процессных шагов, узких мест, потенциала автоматизации, сильных/слабых сторон.
- Ответ содержит РОВНО 3 раздела: Интерпретация, SWOT, Рекомендации. Ничего больше.

Уровни зрелости (ориентир):
1. Начальный (0-20%): ИИ хаотично. Назначить ответственных, зафиксировать метрики, quick wins.
2. AI-Enabled (21-40%): ИИ локально. Стратегия, центр компетенций, ROI.
3. AI-Driven (41-60%): ИИ в процессах. Масштабировать, AgentOps/MLOps/Governance.
4. AI-First (61-80%): ИИ в операционной модели. Автономность, ИИ-платформа, KPI, R&D.
5. AI-Native (81-100%): ИИ — основа бизнеса. Собственные модели, новые рынки, выручка от ИИ.
"""

USER_PROMPT_TEMPLATE = """Результаты диагностики AI-зрелости компании:

Общий индекс: {total_percent}%
Уровень зрелости: {maturity_level}
Надежность результата: {reliability}

Результаты по категориям:
{categories_text}

Сильные стороны: {strengths_text}
Зоны роста: {weaknesses_text}

Ответы пользователя:
{answers_text}

Дай анализ СТРОГО в этом формате, РОВНО 3 раздела, до 2000 символов. Никаких дополнительных разделов.

📊 Интерпретация
Сплошной текст, 2-3 предложения. Без буллетов. Что зафиксировали по текущему состоянию.

📋 SWOT-анализ
S: текст без буллетов
W: текст без буллетов
O: текст без буллетов
T: текст без буллетов

💡 Рекомендации
🚀 Быстрые шаги (сейчас): начни со стратегии, опиши конкретные процессы. Сплошной текст.
📅 Среднесрочные (1-3 месяца): системные улучшения привязанные к категориям. Сплошной текст.
🎯 Долгосрочные (3-6 месяцев): стратегические инициативы для следующего уровня. Сплошной текст.
"""

FALLBACK_INTERPRETATIONS = {
    "Начальный": (
        "ИИ используется хаотично, в виде отдельных инициатив энтузиастов. "
        "Системного эффекта для бизнеса нет.\n\n"
        "💡 Рекомендации: Определить 3–5 приоритетных процессов для диагностики. "
        "Назначить ответственных за ИИ-направление. "
        "Зафиксировать базовые метрики процессов. "
        "Начать с quick wins, чтобы показать первый эффект и снизить сопротивление."
    ),
    "AI-Enabled": (
        "Компания уже использует ИИ-инструменты в отдельных функциях. "
        "Появляются первые положительные кейсы, растет личная продуктивность, "
        "но процессы компании в целом не меняются.\n\n"
        "💡 Рекомендации: Перейти от инструментов к процессам. "
        "Сформировать ИИ-стратегию и дорожную карту. "
        "Создать центр компетенций. Начать считать ROI. "
        "Запустить обучение для руководителей."
    ),
    "AI-Driven": (
        "ИИ встроен в отдельные ключевые процессы и помогает принимать решения. "
        "Компания получает измеримый эффект, но человек все еще остается узким "
        "горлышком в большинстве операций.\n\n"
        "💡 Рекомендации: Перестраивать процессы под ИИ. "
        "Масштабировать лучшие кейсы. "
        "Внедрить AgentOps, MLOps, Data Governance. "
        "Формировать роли операторов ИИ-систем."
    ),
    "AI-First": (
        "ИИ становится частью операционной модели. Существенная доля процессов "
        "автоматизирована, большинство решений валидируется данными и моделями.\n\n"
        "💡 Рекомендации: Углублять автономность процессов. "
        "Развивать корпоративную ИИ-платформу. "
        "Встраивать ИИ в KPI руководителей. "
        "Начинать формировать собственный R&D-контур."
    ),
    "AI-Native": (
        "ИИ является основой бизнес-модели и операционного ядра компании. "
        "Большинство процессов работает как интеллектуальная система.\n\n"
        "💡 Рекомендации: Развивать собственные модели, R&D и научные партнерства. "
        "Масштабировать лучшие практики в новые рынки. "
        "Делать ИИ источником новой выручки."
    ),
}


class LLMService:
    @staticmethod
    def build_user_prompt(result: dict, answers: List[dict], questions_map: dict) -> str:
        categories_text = "\n".join(
            f"  {c['emoji']} {c['name']}: {c['percent']}%"
            + (" (ориентировочно)" if c.get("tentative") else "")
            for c in result["categories"]
        )
        strengths_text = ", ".join(
            f"{s['emoji']} {s['name']} ({s['percent']}%)" for s in result["strengths"]
        )
        weaknesses_text = ", ".join(
            f"{w['emoji']} {w['name']} ({w['percent']}%)" for w in result["weaknesses"]
        )
        answers_lines = []
        for ans in answers:
            q = questions_map.get(ans["question_code"])
            if not q:
                continue
            if ans["is_unknown"]:
                answers_lines.append(f"  {q['text']} → Не знаю")
            else:
                idx = (ans["score"] or 1) - 1
                answers_lines.append(f"  {q['text']} → {q['options'][idx]}")
        answers_text = "\n".join(answers_lines)

        return USER_PROMPT_TEMPLATE.format(
            total_percent=result["total_percent"],
            maturity_level=result["maturity_level"],
            reliability=result["reliability"],
            categories_text=categories_text,
            strengths_text=strengths_text,
            weaknesses_text=weaknesses_text,
            answers_text=answers_text,
        )

    async def generate_analysis(self, result: dict, answers: List[dict]) -> Optional[str]:
        if not config.LLM_API_KEY:
            logger.warning("LLM_API_KEY not set, skipping LLM analysis")
            return None

        questions_map = {q["code"]: q for q in QUESTIONS}
        user_prompt = self.build_user_prompt(result, answers, questions_map)

        try:
            client = AsyncOpenAI(
                api_key=config.LLM_API_KEY,
                base_url=config.LLM_BASE_URL,
            )
            response = await client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_completion_tokens=1500,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return None

    @staticmethod
    def get_fallback_analysis(maturity_level: str) -> str:
        interpretation = FALLBACK_INTERPRETATIONS.get(
            maturity_level,
            "Расширенный анализ временно недоступен.",
        )
        return (
            f"📊 Интерпретация\n{interpretation}\n\n"
            "⚠️ Расширенный анализ (SWOT, рекомендации, дорожная карта) временно недоступен. "
            "Числовой результат сохранен."
        )
