"""
Reusable validation functions for auth, expenses, and uploads.
"""

import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

VALID_CATEGORIES = {
    "Food", "Transport", "Shopping", "Bills", "Entertainment",
    "Education", "Health", "Travel", "Rent", "Other",
}

VALID_PAYMENT_METHODS = {
    "Cash", "UPI", "Debit Card", "Credit Card", "Bank Transfer",
}

ALLOWED_RECEIPT_EXTENSIONS = {"jpg", "jpeg", "png", "pdf"}
MAX_UPLOAD_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def is_valid_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def is_valid_password(password: str) -> tuple:
    """Returns (is_valid, message)."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


def validate_registration(data: dict) -> list:
    """Validates registration payload. Returns a list of error strings."""
    errors = []
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not full_name:
        errors.append("Full name is required.")
    if not email:
        errors.append("Email is required.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")

    valid_pw, pw_msg = is_valid_password(password)
    if not valid_pw:
        errors.append(pw_msg)
    if password != confirm_password:
        errors.append("Passwords do not match.")

    return errors


def validate_login(data: dict) -> list:
    errors = []
    if not (data.get("email") or "").strip():
        errors.append("Email is required.")
    if not data.get("password"):
        errors.append("Password is required.")
    return errors


def validate_expense(data: dict) -> list:
    """Validates an expense payload. Returns a list of error strings."""
    errors = []

    amount = data.get("amount")
    try:
        amount_val = float(amount)
        if amount_val <= 0:
            errors.append("Amount must be greater than 0.")
    except (TypeError, ValueError):
        errors.append("Amount must be a valid number.")

    category = data.get("category")
    if category not in VALID_CATEGORIES:
        errors.append(f"Category must be one of: {', '.join(sorted(VALID_CATEGORIES))}.")

    if not (data.get("date") or "").strip():
        errors.append("Date is required.")

    payment_method = data.get("payment_method")
    if payment_method not in VALID_PAYMENT_METHODS:
        errors.append(f"Payment method must be one of: {', '.join(sorted(VALID_PAYMENT_METHODS))}.")

    description = (data.get("description") or "").strip()
    if len(description) > 500:
        errors.append("Description must be under 500 characters.")

    return errors


def is_allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_RECEIPT_EXTENSIONS


def is_file_size_allowed(size_bytes: int) -> bool:
    return 0 < size_bytes <= MAX_UPLOAD_SIZE_BYTES


def sanitize_string(value: str, max_length: int = 500) -> str:
    if not value:
        return ""
    value = str(value).strip()
    # Strip characters commonly used in injection attempts
    value = re.sub(r"[<>]", "", value)
    return value[:max_length]
