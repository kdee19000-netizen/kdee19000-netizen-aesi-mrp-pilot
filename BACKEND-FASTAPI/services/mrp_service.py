"""
MRP Service

Executes Material Requirements Planning calculations against current
inventory levels and the Bill of Materials.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from models.bom import BillOfMaterials
from models.inventory import Inventory
from models.mrp_run import MRPRun, MRPStatus


class MRPService:
    @staticmethod
    def trigger_run(db: Session, triggered_by: str, items: Optional[List[str]] = None) -> MRPRun:
        """Create a new MRP run record and execute calculations."""
        run = MRPRun(
            id=str(uuid.uuid4()),
            started_at=datetime.utcnow(),
            status=MRPStatus.RUNNING,
            triggered_by=triggered_by,
            planned_orders=[],
            errors=[],
        )
        db.add(run)
        db.commit()

        try:
            planned_orders, errors = MRPService._calculate(db, items)
            run.status = MRPStatus.COMPLETED
            run.planned_orders = planned_orders
            run.errors = errors
            run.items_processed = len(planned_orders)
        except Exception as exc:
            run.status = MRPStatus.FAILED
            run.errors = [str(exc)]

        run.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def _calculate(db: Session, items: Optional[List[str]] = None):
        """
        Simple MRP netting calculation.

        For each inventory item below reorder point, generates a planned order.
        """
        query = db.query(Inventory)
        if items:
            query = query.filter(Inventory.sku.in_(items))

        planned_orders = []
        errors = []

        for inv in query.all():
            available = (inv.quantity_on_hand or 0) - (inv.quantity_reserved or 0)
            if inv.reorder_point and available < inv.reorder_point:
                qty_needed = (inv.max_stock or inv.reorder_point * 2) - available
                if qty_needed > 0:
                    planned_orders.append(
                        {
                            "sku": inv.sku,
                            "name": inv.name,
                            "qty_available": available,
                            "qty_needed": qty_needed,
                            "unit": inv.unit,
                        }
                    )

        return planned_orders, errors
