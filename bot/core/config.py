"""
Bot configuration.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

import os

from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SERVICE_BASE_URL: str = os.getenv("SERVICE_BASE_URL", "http://localhost:8000")
    API_PREFIX: str = "/api/v1"

    @property
    def api_url(self) -> str:
        return f"{self.SERVICE_BASE_URL.rstrip('/')}{self.API_PREFIX}"


config = BotConfig()
