"""
API v1 endpoints для отчётов.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC005
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from service.assessment.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])
report_service = ReportService()


@router.get("/{report_id}", response_class=HTMLResponse)
async def get_report(report_id: str):
    html = report_service.read_report(report_id)
    if not html:
        raise HTTPException(status_code=404, detail="Report not found")
    return HTMLResponse(content=html)
