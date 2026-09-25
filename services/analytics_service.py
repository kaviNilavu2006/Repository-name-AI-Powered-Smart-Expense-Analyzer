"""
Analytics Service
------------------
Computes summary statistics, category breakdowns, and monthly trends
from a user's expense list. Used by both the analytics dashboard and
the AI analysis feature (which needs a structured summary to send to
Bedrock).
"""

import datetime
from collections import defaultdict

from utils.helpers import safe_float, month_key_from_date


class AnalyticsService:
    def build_summary(self, expenses: list) -> dict:
        """Builds the full analytics summary used across the app."""
        total_spending = 0.0
        category_totals = defaultdict(float)
        monthly_totals = defaultdict(float)
        payment_method_totals = defaultdict(float)
        daily_totals = defaultdict(float)
        amounts = []

        for exp in expenses:
            amount = safe_float(exp.get("amount"))
            total_spending += amount
            amounts.append(amount)

            category = exp.get("category", "Other")
            category_totals[category] += amount

            date_str = exp.get("date", "")
            month_key = month_key_from_date(date_str)
            if month_key:
                monthly_totals[month_key] += amount
            if date_str:
                daily_totals[date_str] += amount

            method = exp.get("payment_method", "Other")
            payment_method_totals[method] += amount

        transaction_count = len(expenses)
        avg_transaction = (total_spending / transaction_count) if transaction_count else 0
        highest_expense = max(amounts) if amounts else 0
        lowest_expense = min(amounts) if amounts else 0

        top_category = "N/A"
        top_category_amount = 0
        if category_totals:
            top_category, top_category_amount = max(
                category_totals.items(), key=lambda x: x[1]
            )

        num_days_with_data = len(daily_totals) or 1
        avg_daily_spending = total_spending / num_days_with_data

        current_month_key = datetime.date.today().strftime("%Y-%m")
        this_month_total = monthly_totals.get(current_month_key, 0)

        category_percentages = {
            cat: round((amt / total_spending) * 100, 1) if total_spending else 0
            for cat, amt in category_totals.items()
        }

        recent_expenses = sorted(
            expenses, key=lambda e: e.get("created_at", ""), reverse=True
        )[:10]

        return {
            "total_spending": round(total_spending, 2),
            "this_month_total": round(this_month_total, 2),
            "transaction_count": transaction_count,
            "average_transaction_value": round(avg_transaction, 2),
            "average_daily_spending": round(avg_daily_spending, 2),
            "highest_expense": round(highest_expense, 2),
            "lowest_expense": round(lowest_expense, 2),
            "top_category": top_category,
            "top_category_amount": round(top_category_amount, 2),
            "category_totals": {k: round(v, 2) for k, v in category_totals.items()},
            "category_percentages": category_percentages,
            "monthly_totals": {k: round(v, 2) for k, v in monthly_totals.items()},
            "daily_totals": {k: round(v, 2) for k, v in daily_totals.items()},
            "payment_method_totals": {k: round(v, 2) for k, v in payment_method_totals.items()},
            "recent_expenses": recent_expenses,
        }

    def filter_by_period(self, expenses: list, period: str) -> list:
        """
        period: 'current_month' | 'previous_month' | 'last_3_months' | 'current_year'
        """
        today = datetime.date.today()

        def in_month(date_str, year, month):
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                return d.year == year and d.month == month
            except ValueError:
                return False

        if period == "current_month":
            return [e for e in expenses if in_month(e.get("date", ""), today.year, today.month)]

        if period == "previous_month":
            first_of_month = today.replace(day=1)
            prev_month_last_day = first_of_month - datetime.timedelta(days=1)
            return [
                e for e in expenses
                if in_month(e.get("date", ""), prev_month_last_day.year, prev_month_last_day.month)
            ]

        if period == "last_3_months":
            cutoff = today - datetime.timedelta(days=90)
            result = []
            for e in expenses:
                try:
                    d = datetime.datetime.strptime(e.get("date", ""), "%Y-%m-%d").date()
                    if d >= cutoff:
                        result.append(e)
                except ValueError:
                    continue
            return result

        if period == "current_year":
            result = []
            for e in expenses:
                try:
                    d = datetime.datetime.strptime(e.get("date", ""), "%Y-%m-%d").date()
                    if d.year == today.year:
                        result.append(e)
                except ValueError:
                    continue
            return result

        return expenses


analytics_service = AnalyticsService()
