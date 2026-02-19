"""Risk management router."""

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas.risk import InterventionRequest, RiskResponse, RiskSignal
from services.risk_service import RiskService

router = APIRouter(prefix="/api/risk", tags=["Risk Management"])


@router.post("/signal", response_model=RiskResponse)
async def create_risk_signal(
    signal: RiskSignal,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Quantum-secure risk intake with 10-minute MRP timer."""
    record = await RiskService.create_signal(db, signal, background_tasks)
    return RiskResponse(
        id=record.id,
        user_id=record.user_id,
        risk_score=record.risk_score,
        status=record.status,
        content_hash=record.content_hash,
        created_at=record.created_at,
        quantum_signed=True,
        mrp_timer_started=True,
    )


@router.post("/intervention")
async def handle_intervention(
    intervention: InterventionRequest,
    db: Session = Depends(get_db),
):
    """Human intervention to resolve a pending risk record."""
    return await RiskService.handle_intervention(db, intervention)


@router.get("/{record_id}", tags=["Risk Management"])
def get_risk_record(record_id: str, db: Session = Depends(get_db)):
    """Retrieve a risk record by ID."""
    from fastapi import HTTPException
    from models.risk_record import RiskRecord

    record = db.query(RiskRecord).filter(RiskRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Risk record not found")
    return record
