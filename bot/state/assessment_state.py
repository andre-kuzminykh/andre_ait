"""
In-memory state for assessment flow.

## Трассируемость
Feature: F001 — AI Maturity Assessment

Not critical — backend DB is the source of truth.
"""

# Current assessment ID per telegram user ID
current_assessment: dict[int, int] = {}

# Analysis message IDs per telegram user ID (for cleanup on restart)
analysis_messages: dict[int, list[int]] = {}
