"""
AI-Powered Smart Expense Analyzer
-----------------------------------
Main Flask application entry point.

Run locally with:
    python app.py
or:
    flask run

The Flask app serves both the REST API and the HTML frontend
(templates), so a single deployment (e.g. AWS Elastic Beanstalk)
hosts the entire application.
"""

import os
import logging
from flask import Flask, render_template, session, redirect, url_for, send_from_directory, request
from config.config import get_config

logging.basicConfig(level=logging.INFO)

Config = get_config()

app = Flask(__name__)
app.config.from_object(Config)

# ----------------------------------------------------------------------
# Register API blueprints
# ----------------------------------------------------------------------
from routes.auth_routes import auth_bp
from routes.expense_routes import expense_bp
from routes.analytics_routes import analytics_bp
from routes.ai_routes import ai_bp
from routes.upload_routes import upload_bp

app.register_blueprint(auth_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(upload_bp)


# ----------------------------------------------------------------------
# Local receipt serving (only used when S3 fallback is active)
# ----------------------------------------------------------------------
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    # Local receipt serving is intentionally disabled in production.
    # Production receipts are private S3 objects exposed only through
    # short-lived presigned URLs.
    if not Config.USE_LOCAL_STORAGE_FALLBACK:
        return {"success": False, "error": "Not found."}, 404
    return send_from_directory(Config.LOCAL_UPLOAD_FOLDER, filename)


@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if Config.FLASK_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# ----------------------------------------------------------------------
# Frontend page routes
# ----------------------------------------------------------------------
def _login_required_page():
    return "user_id" not in session


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/login")
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/register")
def register_page():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("dashboard.html", full_name=session.get("full_name"))


@app.route("/add-expense")
def add_expense_page():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("add-expense.html", full_name=session.get("full_name"))


@app.route("/expenses")
def expenses_page():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("expenses.html", full_name=session.get("full_name"))


@app.route("/analytics")
def analytics_page():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("analytics.html", full_name=session.get("full_name"))


@app.route("/ai-insights")
def ai_insights_page():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("ai-insights.html", full_name=session.get("full_name"))


@app.route("/profile")
def profile_page():
    if _login_required_page():
        return redirect(url_for("login_page"))
    return render_template("profile.html", full_name=session.get("full_name"), email=session.get("email"))


# ----------------------------------------------------------------------
# Error handlers
# ----------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html"), 404


@app.errorhandler(500)
def server_error(e):
    logging.error("Server error: %s", e)
    return {"success": False, "error": "An internal server error occurred."}, 500


@app.errorhandler(413)
def request_entity_too_large(e):
    if request.path.startswith("/api/"):
        return {"success": False, "error": "Receipt file size must not exceed 5 MB."}, 400
    return "Request entity too large.", 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=Config.DEBUG)
