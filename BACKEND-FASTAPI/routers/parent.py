"""Parent portal router – read-only access to risk records."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas.risk import RiskResponse
from services.parent_portal_service import ParentPortalService

router = APIRouter(prefix="/api/parent", tags=["Parent Portal"])


@router.get("/{parent_id}/records")
def get_parent_records(
    parent_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Return all risk records linked to a parent/guardian."""
    records = ParentPortalService.get_records_for_parent(db, parent_id, limit, skip)
    return records


@router.get("/{parent_id}/records/{record_id}")
def get_parent_record(
    parent_id: str,
    record_id: str,
    db: Session = Depends(get_db),
):
    """Return a specific risk record for a parent/guardian."""
    record = ParentPortalService.get_record(db, record_id, parent_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found or access denied")
    return record
