"""
ScoringService — детерминистический расчёт результатов диагностики.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC003

## Бизнес-контекст
Рассчитывает индекс зрелости, уровень, надёжность,
результаты по категориям, сильные и слабые стороны.

## Зависимости
- data.assessment.question_bank
"""

from typing import Dict, List

from data.assessment.question_bank import CATEGORIES, QUESTIONS


MATURITY_LEVELS = [
    (0, 20, "Начальный"),
    (21, 40, "AI-Enabled"),
    (41, 60, "AI-Driven"),
    (61, 80, "AI-First"),
    (81, 100, "AI-Native"),
]


class ScoringService:
    @staticmethod
    def get_maturity_level(percent: float) -> str:
        for low, high, label in MATURITY_LEVELS:
            if low <= percent <= high:
                return label
        return "AI-Native"

    @staticmethod
    def get_reliability(unknown_count: int) -> str:
        if unknown_count <= 3:
            return "Высокая"
        elif unknown_count <= 8:
            return "Средняя"
        else:
            return "Низкая"

    def calculate_results(self, answers: List[Dict]) -> Dict:
        """Calculate full assessment results from a list of answer dicts."""
        cat_answers: Dict[str, List[int]] = {}
        unknown_count = 0

        for ans in answers:
            cat = ans["category_code"]
            if cat not in cat_answers:
                cat_answers[cat] = []
            if ans["is_unknown"]:
                unknown_count += 1
            elif ans["score"] is not None:
                cat_answers[cat].append(ans["score"])

        categories_result = []
        for cat in CATEGORIES:
            code = cat["code"]
            scores = cat_answers.get(code, [])
            valid_count = len(scores)
            total_in_cat = len([q for q in QUESTIONS if q["category"] == code])
            unknown_in_cat = sum(
                1 for a in answers
                if a["category_code"] == code and a["is_unknown"]
            )

            if valid_count > 0:
                avg = sum(scores) / valid_count
                percent = round(((avg - 1) / 4) * 100, 1)
            else:
                avg = 0.0
                percent = 0.0

            is_tentative = valid_count < 3

            categories_result.append({
                "code": code,
                "name": cat["name"],
                "emoji": cat["emoji"],
                "weight": cat["weight"],
                "avg": round(avg, 2),
                "percent": percent,
                "valid_count": valid_count,
                "total_count": total_in_cat,
                "unknown_count": unknown_in_cat,
                "tentative": is_tentative,
            })

        weighted_sum = 0.0
        weight_sum = 0.0
        for cr in categories_result:
            if cr["valid_count"] > 0:
                weighted_sum += cr["avg"] * cr["weight"]
                weight_sum += cr["weight"]

        if weight_sum > 0:
            weighted_avg = weighted_sum / weight_sum
            total_percent = round(((weighted_avg - 1) / 4) * 100, 1)
        else:
            weighted_avg = 0.0
            total_percent = 0.0

        maturity_level = self.get_maturity_level(total_percent)
        reliability = self.get_reliability(unknown_count)

        sorted_cats = sorted(
            [c for c in categories_result if c["valid_count"] > 0],
            key=lambda c: c["percent"],
            reverse=True,
        )
        strengths = sorted_cats[:3]
        weaknesses = sorted(
            [c for c in categories_result if c["valid_count"] > 0],
            key=lambda c: c["percent"],
        )[:3]

        return {
            "total_percent": total_percent,
            "weighted_avg": round(weighted_avg, 2),
            "maturity_level": maturity_level,
            "reliability": reliability,
            "unknown_count": unknown_count,
            "categories": categories_result,
            "strengths": [
                {"name": s["name"], "emoji": s["emoji"], "percent": s["percent"]}
                for s in strengths
            ],
            "weaknesses": [
                {"name": w["name"], "emoji": w["emoji"], "percent": w["percent"]}
                for w in weaknesses
            ],
        }
