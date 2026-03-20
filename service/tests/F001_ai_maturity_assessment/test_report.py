"""Tests for HTML report generation."""

import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from service.assessment.report_service import ReportService
from service.assessment.scoring_service import ScoringService
from data.assessment.question_bank import QUESTIONS

scoring = ScoringService()
report_svc = ReportService()


def _make_answer(question_code, category_code, score, is_unknown=False):
    return {
        "question_code": question_code,
        "category_code": category_code,
        "score": score,
        "is_unknown": is_unknown,
        "option_value": score,
    }


def _sample_result():
    answers = [_make_answer(q["code"], q["category"], 3) for q in QUESTIONS]
    return scoring.calculate_results(answers)


def test_report_returns_valid_html():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert html.startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_report_has_dark_mode():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert 'class="dark"' in html
    assert "theme-toggle" in html


def test_report_has_tailwind():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "cdn.tailwindcss.com" in html


def test_report_has_jetbrains_mono():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "JetBrains Mono" in html


def test_report_has_brand_colors():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "#8854F3" in html
    assert "#F97316" in html


def test_report_contains_results():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "50.0%" in html
    assert "AI-Driven" in html


def test_report_contains_categories():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "Стратегия" in html
    assert "Данные" in html
    assert "Внедрение" in html


def test_report_has_progress_bars():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "from-brand-purple to-brand-orange" in html
    assert "rounded-full" in html


def test_report_contains_analysis():
    result = _sample_result()
    analysis = "📊 Интерпретация\nТестовый анализ компании."
    html = report_svc.generate_html_report(result, analysis)
    assert "Тестовый анализ компании" in html


def test_report_without_analysis():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "<!DOCTYPE html>" in html
    assert "50.0%" in html


def test_report_has_no_pdf_button():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "Сохранить как PDF" not in html


def test_report_has_print_css():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "@media print" in html


def test_report_has_og_meta_tags():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert 'og:title' in html
    assert 'og:description' in html
    assert 'og:image' in html


def test_report_has_andre_ai_branding():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "Andre AI" in html
    assert "Technologies" in html


def test_report_has_animated_blobs():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "blob-purple" in html
    assert "blob-orange" in html
    assert "animateBlobs" in html


def test_text_to_html_headers():
    text = "📊 Заголовок\nОбычный текст"
    html = ReportService._text_to_html(text)
    assert "<h3" in html
    assert "<p" in html


def test_text_to_html_list_items():
    text = "- пункт один\n• пункт два"
    html = ReportService._text_to_html(text)
    assert "<li" in html
    assert "пункт один" in html
    assert "пункт два" in html


def test_text_to_html_process_chain():
    text = "[Этап 1: Стратегия] → [Этап 2: Данные]"
    html = ReportService._text_to_html(text)
    assert "process-chain" in html


def test_report_escapes_html():
    result = _sample_result()
    analysis = "Тест <script>alert('xss')</script>"
    html = report_svc.generate_html_report(result, analysis)
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_text_to_html_sub_header_only_label_bold():
    """Sub-headers (🚀/📅/🎯) should only bold the label up to colon."""
    text = "🚀 Быстрые шаги (сейчас): начните со стратегии монетизации."
    html = ReportService._text_to_html(text)
    assert '<span class="font-bold">' in html
    assert "начните со стратегии монетизации" in html
    assert "font-bold\">🚀 Быстрые шаги (сейчас):</span>" in html


def test_text_to_html_section_header_fully_bold():
    """Section headers (📊/📋/💡) should be fully bold."""
    text = "📊 Интерпретация"
    html = ReportService._text_to_html(text)
    assert "font-bold" in html
    assert "<h3" in html


def test_report_strengths_and_weaknesses():
    result = _sample_result()
    html = report_svc.generate_html_report(result, None)
    assert "Сильные стороны" in html
    assert "Зоны роста" in html


def test_report_url_with_production_domain():
    """Report URL should use REPORT_BASE_URL from config (production domain)."""
    svc = ReportService()
    with patch("service.assessment.report_service.config") as mock_config:
        mock_config.REPORT_BASE_URL = "https://andre.technology"
        url = svc.get_report_url("abc123def456")
    assert url == "https://andre.technology/api/v1/reports/abc123def456"


def test_report_url_with_localhost():
    """Report URL should work with localhost for local development."""
    svc = ReportService()
    with patch("service.assessment.report_service.config") as mock_config:
        mock_config.REPORT_BASE_URL = "http://localhost:8000"
        url = svc.get_report_url("abc123def456")
    assert url == "http://localhost:8000/api/v1/reports/abc123def456"


def test_report_url_strips_trailing_slash():
    """Report URL should handle trailing slash in REPORT_BASE_URL."""
    svc = ReportService()
    with patch("service.assessment.report_service.config") as mock_config:
        mock_config.REPORT_BASE_URL = "https://andre.technology/"
        url = svc.get_report_url("abc123def456")
    assert url == "https://andre.technology/api/v1/reports/abc123def456"


def test_report_save_and_read():
    """Saved report should be readable by ID."""
    svc = ReportService()
    html = "<html><body>Test</body></html>"
    report_id = svc.save_report(html)
    assert len(report_id) == 12
    assert all(c in "0123456789abcdef" for c in report_id)
    content = svc.read_report(report_id)
    assert content == html
    # cleanup
    path = svc.get_report_path(report_id)
    if path:
        os.remove(path)


def test_report_invalid_id_returns_none():
    """Invalid report_id should return None."""
    svc = ReportService()
    assert svc.get_report_path("invalid!@#") is None
    assert svc.read_report("nonexistent123") is None
