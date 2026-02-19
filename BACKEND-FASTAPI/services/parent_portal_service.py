"""
Parent Portal Service

Provides read-only access to risk records for authorised parents/guardians.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from models.risk_record import RiskRecord


class ParentPortalService:
    @staticmethod
    def get_records_for_parent(
        db: Session,
        parent_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[RiskRecord]:
        """Return risk records linked to a parent/guardian ID."""
        return (
            db.query(RiskRecord)
            .filter(RiskRecord.parent_id == parent_id)
            .order_by(RiskRecord.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_record(db: Session, record_id: str, parent_id: str) -> Optional[RiskRecord]:
        """Return a specific record, verifying parent ownership."""
        return (
            db.query(RiskRecord)
            .filter(RiskRecord.id == record_id, RiskRecord.parent_id == parent_id)
            .first()
        )
