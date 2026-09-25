"""
AI Routes
----------
GET  /api/ai/analyze
POST /api/ai/chat
"""

from flask import Blueprint, request

from services.dynamodb_service import dynamodb_service
from services.analytics_service import analytics_service
from services.bedrock_service import bedrock_service
from utils.helpers import login_required, get_current_user_id, json_success, json_error

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")


@ai_bp.route("/analyze", methods=["GET"])
@login_required
def analyze():
    user_id = get_current_user_id()
    expenses = dynamodb_service.list_expenses_for_user(user_id)

    if not expenses:
        return json_success(data={
            "source": "none",
            "analysis": "Add some expenses first, then come back here for AI-powered insights!",
            "disclaimer": "",
        })

    summary = analytics_service.build_summary(expenses)
    result = bedrock_service.analyze_expenses(summary)
    return json_success(data=result)


@ai_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    user_id = get_current_user_id()
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return json_error("Please enter a message.", 400)

    # Ownership is enforced here: only the logged-in user's own
    # expenses are ever used as AI context. No cross-user data access.
    expenses = dynamodb_service.list_expenses_for_user(user_id)
    summary = analytics_service.build_summary(expenses)

    result = bedrock_service.chat(message, summary)
    return json_success(data=result)
