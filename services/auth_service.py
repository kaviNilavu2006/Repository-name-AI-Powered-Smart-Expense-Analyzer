"""
Auth Service
------------
Handles user registration, login verification, and password hashing.
Passwords are never stored in plain text.
"""

import json
import os

from werkzeug.security import generate_password_hash, check_password_hash

from services.dynamodb_service import dynamodb_service
from utils.helpers import generate_id, current_timestamp
from config.config import get_config

Config = get_config()

SAMPLE_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "sample_data",
    "sample_expenses.json",
)


class AuthService:
    def _seed_demo_expenses(self, user_id: str) -> None:
        """
        In DEMO_MODE, every newly-registered user gets a copy of the
        sample expenses so the dashboard/analytics/charts aren't empty
        on first login. No-op if DEMO_MODE is off or the sample file
        is missing.
        """
        if not getattr(Config, "DEMO_MODE", False):
            return

        try:
            with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as fh:
                sample_expenses = json.load(fh)
        except (OSError, json.JSONDecodeError):
            return

        for sample in sample_expenses:
            expense_item = {
                **sample,
                "expense_id": generate_id("exp_"),
                "user_id": user_id,
                "receipt_key": sample.get("receipt_key", ""),
                "receipt_url": sample.get("receipt_url", ""),
                "created_at": current_timestamp(),
            }
            dynamodb_service.create_expense(expense_item)

    def register_user(self, full_name: str, email: str, password: str) -> dict:
        """
        Creates a new user record. Raises ValueError if the email is
        already registered.
        """
        email = email.strip().lower()
        existing = dynamodb_service.get_user_by_email(email)
        if existing:
            raise ValueError("An account with this email already exists.")

        user_item = {
            "user_id": generate_id("user_"),
            "full_name": full_name.strip(),
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": current_timestamp(),
        }
        dynamodb_service.create_user(user_item)
        self._seed_demo_expenses(user_item["user_id"])

        # Never return the password hash to callers
        safe_user = {k: v for k, v in user_item.items() if k != "password_hash"}
        return safe_user

    def verify_login(self, email: str, password: str) -> dict:
        """
        Verifies credentials. Returns the safe user dict on success.
        Raises ValueError on invalid credentials.
        """
        email = email.strip().lower()
        user = dynamodb_service.get_user_by_email(email)
        if not user:
            raise ValueError("Invalid email or password.")

        if not check_password_hash(user["password_hash"], password):
            raise ValueError("Invalid email or password.")

        return {k: v for k, v in user.items() if k != "password_hash"}

    def get_user_profile(self, user_id: str):
        user = dynamodb_service.get_user_by_id(user_id)
        if not user:
            return None
        return {k: v for k, v in user.items() if k != "password_hash"}


auth_service = AuthService()
