"""
Подключение роутеров к FastAPI-приложению.

## Трассируемость
Feature: F001 — AI Maturity Assessment
"""

from fastapi import FastAPI

from api.v1.endpoints.assessments.assessment_endpoint import router as assessment_router
from api.v1.endpoints.assessments.question_endpoint import router as question_router
from api.v1.endpoints.reports.report_endpoint import router as report_router


def include_routers(app: FastAPI):
    prefix = "/api/v1"
    app.include_router(assessment_router, prefix=prefix)
    app.include_router(question_router, prefix=prefix)
    app.include_router(report_router, prefix=prefix)
