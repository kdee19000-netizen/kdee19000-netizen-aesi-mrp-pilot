"""MRP workflow router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import get_db
from schemas.mrp import MRPRunResponse, MRPTrigger
from services.mrp_service import MRPService

router = APIRouter(prefix="/api/mrp", tags=["MRP"])


@router.post("/run", response_model=MRPRunResponse)
def trigger_mrp_run(trigger: MRPTrigger, db: Session = Depends(get_db)):
    """Trigger a new MRP calculation run."""
    return MRPService.trigger_run(db, trigger.triggered_by, trigger.items)


@router.get("/run/{run_id}", response_model=MRPRunResponse)
def get_mrp_run(run_id: str, db: Session = Depends(get_db)):
    """Retrieve the status and results of an MRP run."""
    from fastapi import HTTPException
    from models.mrp_run import MRPRun

    run = db.query(MRPRun).filter(MRPRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="MRP run not found")
    return run
