"""
Tests for authentication: registration and login flows.
Run with: pytest tests/test_auth.py
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def unique_email():
    import uuid
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


def test_register_success(client):
    email = unique_email()
    response = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["user"]["email"] == email


def test_register_password_mismatch(client):
    response = client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": unique_email(),
        "password": "password123",
        "confirm_password": "different",
    })
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_register_duplicate_email(client):
    email = unique_email()
    payload = {
        "full_name": "Test User",
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
    }
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409


def test_login_success(client):
    email = unique_email()
    client.post("/api/auth/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "password123",
        "confirm_password": "password123",
    })
    response = client.post("/api/auth/login", json={
        "email": email,
        "password": "password123",
    })
    assert response.status_code == 200
    assert response.get_json()["success"] is True


def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.get_json()["success"] is False
