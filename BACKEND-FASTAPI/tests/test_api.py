"""
FastAPI integration tests using TestClient.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Point to a shared file-based SQLite so that the app's engine and the
# test session see the same data.  Set timer to 0 to avoid the 10-min wait.
_TEST_DB = "sqlite:///./test_aesi_mrp.db"
os.environ.setdefault("DATABASE_URL", _TEST_DB)
os.environ["MRP_TIMER_SECONDS"] = "0"

import models.base as _base  # noqa: E402 – must come after env-var is set

from models.base import Base
from dependencies import get_db


# ---------------------------------------------------------------------------
# Test database + app fixture
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def client():
    # Re-point the shared engine to a test SQLite file
    test_engine = create_engine(_TEST_DB, connect_args={"check_same_thread": False})
    _base.engine = test_engine
    Base.metadata.create_all(test_engine)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    _base.SessionLocal = TestSessionLocal

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    from main import app

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    # Clean up test DB file
    import pathlib

    pathlib.Path("./test_aesi_mrp.db").unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["quantum_safe"] is True
    assert data["status"] == "operational"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_risk_signal(client):
    payload = {"user_id": "user-123", "content": "urgent help needed", "language": "en"}
    response = client.post("/api/risk/signal", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["quantum_signed"] is True


def test_audit_proof_for_unknown_record(client):
    response = client.get("/api/audit/proof/nonexistent-record-id")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False


def test_audit_chain_for_risk_signal(client):
    # Create a signal first
    payload = {"user_id": "user-456", "content": "test content for audit", "language": "en"}
    create_response = client.post("/api/risk/signal", json=payload)
    record_id = create_response.json()["id"]

    chain_response = client.get(f"/api/audit/chain/{record_id}")
    assert chain_response.status_code == 200
    chain = chain_response.json()
    assert len(chain) >= 1


def test_admin_stats(client):
    response = client.get("/api/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_risk_records" in data
    assert data["quantum_safe"] is True


def test_inventory_list_empty(client):
    response = client.get("/api/inventory/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_inventory_create_and_retrieve(client):
    item = {
        "sku": "TEST-SKU-001",
        "name": "Test Item",
        "quantity_on_hand": 50,
        "reorder_point": 10,
        "unit": "ea",
    }
    create_resp = client.post("/api/inventory/", json=item)
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]

    get_resp = client.get(f"/api/inventory/{item_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["sku"] == "TEST-SKU-001"


def test_mrp_trigger_run(client):
    # Seed an inventory item below reorder point
    item = {
        "sku": "MRP-TEST-SKU",
        "name": "MRP Test Item",
        "quantity_on_hand": 2,
        "reorder_point": 20,
        "max_stock": 100,
        "unit": "ea",
    }
    client.post("/api/inventory/", json=item)

    response = client.post("/api/mrp/run", json={"triggered_by": "test-system"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
