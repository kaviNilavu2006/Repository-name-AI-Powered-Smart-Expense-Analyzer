"""
Expense Routes
---------------
GET    /api/expenses
POST   /api/expenses
GET    /api/expenses/<id>
PUT    /api/expenses/<id>
DELETE /api/expenses/<id>
"""

from flask import Blueprint, request

from services.dynamodb_service import dynamodb_service
from services.s3_service import s3_service
from utils.validators import validate_expense, is_allowed_file, is_file_size_allowed, sanitize_string
from utils.helpers import (
    login_required, get_current_user_id, json_success, json_error,
    generate_id, current_timestamp,
)

expense_bp = Blueprint("expenses", __name__, url_prefix="/api/expenses")


@expense_bp.route("", methods=["GET"])
@login_required
def list_expenses():
    user_id = get_current_user_id()
    expenses = dynamodb_service.list_expenses_for_user(user_id)

    # Optional filters via query params
    category = request.args.get("category")
    search = request.args.get("search", "").lower()
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    sort_by = request.args.get("sort_by", "date")
    order = request.args.get("order", "desc")

    if category and category != "all":
        expenses = [e for e in expenses if e.get("category") == category]

    if search:
        expenses = [
            e for e in expenses
            if search in (e.get("description", "") or "").lower()
        ]

    if date_from:
        expenses = [e for e in expenses if e.get("date", "") >= date_from]
    if date_to:
        expenses = [e for e in expenses if e.get("date", "") <= date_to]

    reverse = order == "desc"
    if sort_by == "amount":
        expenses.sort(key=lambda e: float(e.get("amount", 0)), reverse=reverse)
    else:
        expenses.sort(key=lambda e: e.get("date", ""), reverse=reverse)

    return json_success(data={"expenses": expenses, "count": len(expenses)})


@expense_bp.route("", methods=["POST"])
@login_required
def create_expense():
    user_id = get_current_user_id()
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    errors = validate_expense(data)
    if errors:
        return json_error("; ".join(errors), 400)

    receipt_url = ""
    receipt_key = ""

    uploaded_file = request.files.get("receipt")
    if uploaded_file and uploaded_file.filename:
        if not is_allowed_file(uploaded_file.filename):
            return json_error("Receipt must be a JPG, JPEG, PNG, or PDF file.", 400)

        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
        if not is_file_size_allowed(size):
            return json_error("Receipt file size must not exceed 5 MB.", 400)

        try:
            result = s3_service.upload_receipt(uploaded_file, user_id)
            receipt_key = result["key"]
            receipt_url = result["url"]
        except RuntimeError as exc:
            return json_error(str(exc), 502)

    expense_item = {
        "expense_id": generate_id("exp_"),
        "user_id": user_id,
        "amount": str(data.get("amount")),
        "category": data.get("category"),
        "description": sanitize_string(data.get("description", "")),
        "date": data.get("date"),
        "payment_method": data.get("payment_method"),
        "receipt_url": receipt_url,
        "receipt_key": receipt_key,
        "created_at": current_timestamp(),
    }

    dynamodb_service.create_expense(expense_item)
    return json_success(data={"expense": expense_item}, message="Expense added successfully.", status_code=201)


@expense_bp.route("/<expense_id>", methods=["GET"])
@login_required
def get_expense(expense_id):
    user_id = get_current_user_id()
    expense = dynamodb_service.get_expense(user_id, expense_id)
    if not expense:
        return json_error("Expense not found.", 404)
    return json_success(data={"expense": expense})


@expense_bp.route("/<expense_id>", methods=["PUT"])
@login_required
def update_expense(expense_id):
    user_id = get_current_user_id()
    existing = dynamodb_service.get_expense(user_id, expense_id)
    if not existing:
        return json_error("Expense not found.", 404)

    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    errors = validate_expense({**existing, **data})
    if errors:
        return json_error("; ".join(errors), 400)

    updates = {
        "amount": str(data.get("amount", existing.get("amount"))),
        "category": data.get("category", existing.get("category")),
        "description": sanitize_string(data.get("description", existing.get("description", ""))),
        "date": data.get("date", existing.get("date")),
        "payment_method": data.get("payment_method", existing.get("payment_method")),
    }

    uploaded_file = request.files.get("receipt")
    if uploaded_file and uploaded_file.filename:
        if not is_allowed_file(uploaded_file.filename):
            return json_error("Receipt must be a JPG, JPEG, PNG, or PDF file.", 400)
        uploaded_file.seek(0, 2)
        size = uploaded_file.tell()
        uploaded_file.seek(0)
        if not is_file_size_allowed(size):
            return json_error("Receipt file size must not exceed 5 MB.", 400)
        try:
            result = s3_service.upload_receipt(uploaded_file, user_id)
            updates["receipt_url"] = result["url"]
            updates["receipt_key"] = result["key"]
        except RuntimeError as exc:
            return json_error(str(exc), 502)

    updated = dynamodb_service.update_expense(user_id, expense_id, updates)
    return json_success(data={"expense": updated}, message="Expense updated successfully.")


@expense_bp.route("/<expense_id>", methods=["DELETE"])
@login_required
def delete_expense(expense_id):
    user_id = get_current_user_id()
    existing = dynamodb_service.get_expense(user_id, expense_id)
    if not existing:
        return json_error("Expense not found.", 404)

    if existing.get("receipt_key"):
        s3_service.delete_receipt(existing["receipt_key"])

    dynamodb_service.delete_expense(user_id, expense_id)
    return json_success(message="Expense deleted successfully.")
