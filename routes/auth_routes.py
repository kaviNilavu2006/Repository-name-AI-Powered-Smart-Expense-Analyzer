"""
Authentication Routes
----------------------
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
"""

from flask import Blueprint, request, session

from services.auth_service import auth_service
from utils.validators import validate_registration, validate_login
from utils.helpers import json_success, json_error

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or request.form.to_dict()

    errors = validate_registration(data)
    if errors:
        return json_error("; ".join(errors), 400)

    try:
        user = auth_service.register_user(
            full_name=data.get("full_name"),
            email=data.get("email"),
            password=data.get("password"),
        )
    except ValueError as exc:
        return json_error(str(exc), 409)
    except Exception:
        return json_error("Registration failed due to a server error.", 500)

    session.permanent = True
    session["user_id"] = user["user_id"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]

    return json_success(data={"user": user}, message="Registration successful.", status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or request.form.to_dict()

    errors = validate_login(data)
    if errors:
        return json_error("; ".join(errors), 400)

    try:
        user = auth_service.verify_login(
            email=data.get("email"), password=data.get("password")
        )
    except ValueError as exc:
        return json_error(str(exc), 401)
    except Exception:
        return json_error("Login failed due to a server error.", 500)

    session.permanent = True
    session["user_id"] = user["user_id"]
    session["full_name"] = user["full_name"]
    session["email"] = user["email"]

    return json_success(data={"user": user}, message="Login successful.")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return json_success(message="Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return json_error("Not authenticated.", 401)
    return json_success(data={
        "user_id": session["user_id"],
        "full_name": session.get("full_name"),
        "email": session.get("email"),
    })
