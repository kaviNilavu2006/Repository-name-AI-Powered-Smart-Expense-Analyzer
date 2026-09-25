"""
Tests for expense CRUD operations.
Run with: pytest tests/test_expenses.py
"""

import sys
import os
import uuid
from io import BytesIO
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def logged_in_client(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/api/auth/register", json={
        "full_name": "Expense Tester",
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
    })
    return client


def test_create_expense(logged_in_client):
    response = logged_in_client.post("/api/expenses", data={
        "amount": "500",
        "category": "Food",
        "description": "Lunch",
        "date": "2026-09-01",
        "payment_method": "UPI",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["expense"]["category"] == "Food"


def test_create_expense_invalid_amount(logged_in_client):
    response = logged_in_client.post("/api/expenses", data={
        "amount": "-50",
        "category": "Food",
        "description": "Invalid",
        "date": "2026-09-01",
        "payment_method": "UPI",
    })
    assert response.status_code == 400


def test_get_expenses_requires_login(client):
    response = client.get("/api/expenses")
    assert response.status_code == 401


def test_list_expenses(logged_in_client):
    logged_in_client.post("/api/expenses", data={
        "amount": "200",
        "category": "Transport",
        "description": "Bus fare",
        "date": "2026-09-02",
        "payment_method": "Cash",
    })
    response = logged_in_client.get("/api/expenses")
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"]["count"] >= 1


def test_delete_expense(logged_in_client):
    create_response = logged_in_client.post("/api/expenses", data={
        "amount": "100",
        "category": "Other",
        "description": "To be deleted",
        "date": "2026-09-03",
        "payment_method": "Cash",
    })
    expense_id = create_response.get_json()["data"]["expense"]["expense_id"]

    delete_response = logged_in_client.delete(f"/api/expenses/{expense_id}")
    assert delete_response.status_code == 200

    get_response = logged_in_client.get(f"/api/expenses/{expense_id}")
    assert get_response.status_code == 404


def test_update_expense_rejects_oversized_receipt(logged_in_client):
    create_response = logged_in_client.post("/api/expenses", data={
        "amount": "100",
        "category": "Other",
        "description": "Original expense",
        "date": "2026-09-03",
        "payment_method": "Cash",
    })
    expense_id = create_response.get_json()["data"]["expense"]["expense_id"]

    response = logged_in_client.put(
        f"/api/expenses/{expense_id}",
        data={
            "amount": "100",
            "category": "Other",
            "description": "Original expense",
            "date": "2026-09-03",
            "payment_method": "Cash",
            "receipt": (BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "large.png"),
        },
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
