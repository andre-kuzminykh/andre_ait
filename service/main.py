"""
Точка входа для бэкенд-сервиса AI Maturity Assessment.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

import uvicorn

from core.loader import app  # noqa: F401


if __name__ == "__main__":
    uvicorn.run("core.loader:app", host="0.0.0.0", port=8000, reload=True)
