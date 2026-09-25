"""
General-purpose helper functions used across the application.
"""

import uuid
import datetime
from functools import wraps
from flask import session, jsonify


def generate_id(prefix: str = "") -> str:
    """Generate a unique ID, optionally prefixed (e.g. 'exp_', 'user_')."""
    unique = uuid.uuid4().hex[:12]
    return f"{prefix}{unique}" if prefix else unique


def current_timestamp() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def json_error(message: str, status_code: int = 400):
    """Standard error JSON response. Never leaks internal AWS error details."""
    return jsonify({"success": False, "error": message}), status_code


def json_success(data=None, message: str = None, status_code: int = 200):
    payload = {"success": True}
    if message:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def login_required(f):
    """Decorator to protect API routes that require an authenticated session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return json_error("Unauthorized. Please log in.", 401)
        return f(*args, **kwargs)
    return decorated


def get_current_user_id():
    return session.get("user_id")


def month_key_from_date(date_str: str) -> str:
    """Extracts YYYY-MM from a YYYY-MM-DD date string."""
    try:
        return date_str[:7]
    except Exception:
        return ""


def safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
