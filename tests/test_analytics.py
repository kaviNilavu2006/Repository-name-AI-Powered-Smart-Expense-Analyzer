"""
Tests for the analytics service calculations.
Run with: pytest tests/test_analytics.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.analytics_service import analytics_service

SAMPLE_EXPENSES = [
    {"amount": "500", "category": "Food", "date": "2026-09-01", "payment_method": "UPI", "created_at": "2026-09-01T10:00:00Z"},
    {"amount": "1200", "category": "Transport", "date": "2026-09-02", "payment_method": "Cash", "created_at": "2026-09-02T10:00:00Z"},
    {"amount": "300", "category": "Food", "date": "2026-09-03", "payment_method": "UPI", "created_at": "2026-09-03T10:00:00Z"},
]


def test_build_summary_total():
    summary = analytics_service.build_summary(SAMPLE_EXPENSES)
    assert summary["total_spending"] == 2000.0


def test_build_summary_category_totals():
    summary = analytics_service.build_summary(SAMPLE_EXPENSES)
    assert summary["category_totals"]["Food"] == 800.0
    assert summary["category_totals"]["Transport"] == 1200.0


def test_build_summary_top_category():
    summary = analytics_service.build_summary(SAMPLE_EXPENSES)
    assert summary["top_category"] == "Transport"


def test_build_summary_transaction_count():
    summary = analytics_service.build_summary(SAMPLE_EXPENSES)
    assert summary["transaction_count"] == 3


def test_build_summary_empty():
    summary = analytics_service.build_summary([])
    assert summary["total_spending"] == 0
    assert summary["transaction_count"] == 0
    assert summary["top_category"] == "N/A"


def test_highest_and_lowest_expense():
    summary = analytics_service.build_summary(SAMPLE_EXPENSES)
    assert summary["highest_expense"] == 1200.0
    assert summary["lowest_expense"] == 300.0
