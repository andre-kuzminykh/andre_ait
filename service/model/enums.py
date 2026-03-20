"""
Перечисления для моделей.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

import enum


class AssessmentStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
