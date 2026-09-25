"""
Analytics Routes
-----------------
GET /api/analytics/summary
GET /api/analytics/category
GET /api/analytics/monthly
"""

from flask import Blueprint, request

from services.dynamodb_service import dynamodb_service
from services.analytics_service import analytics_service
from utils.helpers import login_required, get_current_user_id, json_success

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")


def _get_filtered_expenses(user_id):
    expenses = dynamodb_service.list_expenses_for_user(user_id)
    period = request.args.get("period")
    if period:
        expenses = analytics_service.filter_by_period(expenses, period)
    return expenses


@analytics_bp.route("/summary", methods=["GET"])
@login_required
def summary():
    user_id = get_current_user_id()
    expenses = _get_filtered_expenses(user_id)
    data = analytics_service.build_summary(expenses)
    return json_success(data=data)


@analytics_bp.route("/category", methods=["GET"])
@login_required
def category_breakdown():
    user_id = get_current_user_id()
    expenses = _get_filtered_expenses(user_id)
    data = analytics_service.build_summary(expenses)
    return json_success(data={
        "category_totals": data["category_totals"],
        "category_percentages": data["category_percentages"],
    })


@analytics_bp.route("/monthly", methods=["GET"])
@login_required
def monthly_breakdown():
    user_id = get_current_user_id()
    expenses = dynamodb_service.list_expenses_for_user(user_id)  # monthly view uses all data
    data = analytics_service.build_summary(expenses)
    return json_success(data={
        "monthly_totals": data["monthly_totals"],
        "daily_totals": data["daily_totals"],
    })
