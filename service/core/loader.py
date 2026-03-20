"""
FastAPI application factory.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

from fastapi import FastAPI

app = FastAPI(
    title="AI Maturity Assessment API",
    version="1.0.0",
    description="Бэкенд-сервис для диагностики AI-зрелости компаний.",
)


def setup_routers():
    from api.v1.include_router import include_routers
    include_routers(app)


setup_routers()
