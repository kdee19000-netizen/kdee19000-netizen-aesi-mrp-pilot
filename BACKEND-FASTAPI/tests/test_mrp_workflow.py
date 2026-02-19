"""
Tests for the MRP workflow.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.base import Base
from models.inventory import Inventory
from models.mrp_run import MRPRun, MRPStatus
from services.mrp_service import MRPService
import uuid
from datetime import datetime


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed inventory items
    items = [
        Inventory(
            id=str(uuid.uuid4()),
            sku="WIDGET-A",
            name="Widget A",
            quantity_on_hand=5,
            quantity_reserved=0,
            reorder_point=10,
            max_stock=50,
            unit="ea",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Inventory(
            id=str(uuid.uuid4()),
            sku="WIDGET-B",
            name="Widget B",
            quantity_on_hand=100,
            quantity_reserved=0,
            reorder_point=10,
            max_stock=200,
            unit="ea",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    for item in items:
        session.add(item)
    session.commit()

    yield session
    session.close()


def test_mrp_run_created(db):
    run = MRPService.trigger_run(db, triggered_by="test-user")
    assert run.id is not None
    assert run.status == MRPStatus.COMPLETED


def test_mrp_identifies_below_reorder(db):
    """WIDGET-A is below reorder point; should appear in planned_orders."""
    run = MRPService.trigger_run(db, triggered_by="test-user")
    skus = [o["sku"] for o in run.planned_orders]
    assert "WIDGET-A" in skus


def test_mrp_excludes_sufficient_stock(db):
    """WIDGET-B is above reorder point; should NOT appear in planned_orders."""
    run = MRPService.trigger_run(db, triggered_by="test-user")
    skus = [o["sku"] for o in run.planned_orders]
    assert "WIDGET-B" not in skus


def test_mrp_filtered_run(db):
    """A filtered run on WIDGET-B should produce no planned orders."""
    run = MRPService.trigger_run(db, triggered_by="test-user", items=["WIDGET-B"])
    assert run.planned_orders == []


def test_mrp_records_items_processed(db):
    run = MRPService.trigger_run(db, triggered_by="test-user")
    assert run.items_processed >= 1
