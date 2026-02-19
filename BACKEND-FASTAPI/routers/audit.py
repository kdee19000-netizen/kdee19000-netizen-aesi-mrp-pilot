"""Audit chain router."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from models.audit_log import AuditLog
from schemas.audit import AuditLogResponse, AuditProofResponse
from services.audit_service import AuditService

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("/proof/{record_id}", response_model=AuditProofResponse)
def get_audit_proof(record_id: str, db: Session = Depends(get_db)):
    """Return quantum-verified chain integrity proof for a record."""
    result = AuditService.verify_chain(db, record_id)
    return AuditProofResponse(quantum_safe=True, **result)


@router.get("/chain/{record_id}", response_model=List[AuditLogResponse])
def get_audit_chain(record_id: str, db: Session = Depends(get_db)):
    """Return the full ordered audit chain for a record."""
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.record_id == record_id)
        .order_by(AuditLog.timestamp)
        .all()
    )
    return logs
