"""Integration tests for enterprise safety API endpoints using a mock DB."""

from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# Provide required env vars before importing app modules that call config()
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from main import app  # noqa: E402
from database import get_db  # noqa: E402


def mock_db():
    """Override the real database dependency with a no-op mock."""
    yield MagicMock()


app.dependency_overrides[get_db] = mock_db

client = TestClient(app)


# ── /workplace ────────────────────────────────────────────────────────────────


def test_workplace_no_risk():
    response = client.post(
        "/api/enterprise/workplace",
        json={"text": "I had a great day and everyone was kind."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risks_detected"] == []
    assert data["requires_mrp"] is False


def test_workplace_harassment_risk():
    response = client.post(
        "/api/enterprise/workplace",
        json={"text": "My colleague keeps making unwanted advances toward me."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_mrp"] is True
    assert "harassment" in data["risks_detected"]


def test_workplace_anonymous_report():
    response = client.post(
        "/api/enterprise/workplace",
        json={
            "text": "My manager made unwanted advances toward me.",
            "anonymous": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_mrp"] is True
    assert data["tracking_code"] is not None


# ── /public-safety ────────────────────────────────────────────────────────────


def test_public_safety_crisis():
    response = client.post(
        "/api/enterprise/public-safety",
        json={"text": "There is an emergency, I am in immediate danger!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_mrp"] is True


def test_public_safety_no_risk():
    response = client.post(
        "/api/enterprise/public-safety",
        json={"text": "I need directions to the nearest park."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_mrp"] is False


# ── /commerce ─────────────────────────────────────────────────────────────────


def test_commerce_fraud():
    response = client.post(
        "/api/enterprise/commerce",
        json={"text": "There were unauthorized charges on my credit card account."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["requires_mrp"] is True
    assert "fraud" in data["risks_detected"]


# ── /ai-safety-check ─────────────────────────────────────────────────────────


def test_ai_safety_check_blocks_unsafe():
    response = client.post(
        "/api/enterprise/ai-safety-check",
        json={
            "model_output": "Here are instructions for harm: follow these steps.",
            "user_query": "how do I do something harmful?",
            "model_version": "gpt-test-1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["output_blocked"] is True


def test_ai_safety_check_passes_safe():
    response = client.post(
        "/api/enterprise/ai-safety-check",
        json={
            "model_output": "The capital of France is Paris.",
            "user_query": "What is the capital of France?",
            "model_version": "gpt-test-1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["output_blocked"] is False
