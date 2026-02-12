"""
AESI-MRP FastAPI Backend
Provides REST API endpoints for the MRP system.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from backend.mrp_engine import MRPEngine, SignalStatus
from backend.audit_log import AuditLog


# Pydantic models for request/response validation
class SignalSubmission(BaseModel):
    """Model for submitting a new high-risk signal"""
    student_id: str = Field(..., description="Student identifier")
    risk_type: str = Field(..., description="Type of risk detected")
    severity: str = Field(..., description="Severity level (HIGH, CRITICAL)")
    description: str = Field(..., description="Description of the risk")
    detected_by: str = Field(..., description="Detection source/system")
    metadata: Optional[Dict] = Field(default={}, description="Additional metadata")


class InterventionLog(BaseModel):
    """Model for logging an intervention"""
    signal_id: str = Field(..., description="Signal identifier")
    action: str = Field(..., description="Intervention action taken")
    staff_id: str = Field(..., description="Staff member ID")
    notes: Optional[str] = Field(default="", description="Additional notes")


class SignalResponse(BaseModel):
    """Model for signal response"""
    signal_id: str
    status: str
    created_at: str
    data: Dict
    intervention: Optional[str] = None
    resolved_at: Optional[str] = None
    escalated: bool


class AuditEntryResponse(BaseModel):
    """Model for audit entry response"""
    id: int
    signal_id: str
    event_type: str
    timestamp: str
    data: Dict
    hash: str


# Initialize FastAPI app
app = FastAPI(
    title="AESI-MRP API",
    description="API for Automated Escalation & Safety Intelligence - Mandatory Response Protocol",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
audit_log = AuditLog()
mrp_engine = MRPEngine(audit_log)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AESI-MRP API",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = audit_log.get_statistics()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "audit_log_integrity": stats["chain_valid"],
        "total_signals": len(mrp_engine.get_all_signals())
    }


@app.post("/api/signals/submit", status_code=status.HTTP_201_CREATED)
async def submit_signal(signal: SignalSubmission) -> Dict:
    """
    Submit a new high-risk signal.
    Immediately locks the record to PENDING and starts the 10-minute timer.
    """
    try:
        signal_data = signal.model_dump()
        signal_id = mrp_engine.receive_signal(signal_data)
        
        return {
            "signal_id": signal_id,
            "status": "PENDING",
            "message": "Signal received and locked. 10-minute timer started.",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process signal: {str(e)}"
        )


@app.post("/api/signals/intervention")
async def log_intervention(intervention: InterventionLog) -> Dict:
    """
    Log a verified intervention to unlock a PENDING signal.
    """
    intervention_data = {
        "action": intervention.action,
        "staff_id": intervention.staff_id,
        "notes": intervention.notes,
        "logged_at": datetime.utcnow().isoformat()
    }
    
    success = mrp_engine.log_intervention(
        intervention.signal_id, 
        intervention_data
    )
    
    if not success:
        signal = mrp_engine.get_signal(intervention.signal_id)
        if not signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Signal {intervention.signal_id} not found"
            )
        elif signal.status == SignalStatus.ESCALATED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Signal already escalated to Tier 2. Cannot log intervention."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to log intervention"
            )
    
    return {
        "signal_id": intervention.signal_id,
        "status": "RESOLVED",
        "message": "Intervention logged successfully. Signal unlocked.",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/signals/pending")
async def get_pending_signals() -> List[SignalResponse]:
    """
    Get all signals with PENDING status (Compliance Dashboard).
    """
    pending = mrp_engine.get_pending_signals()
    
    return [
        SignalResponse(
            signal_id=record.signal_id,
            status=record.status.value,
            created_at=record.created_at.isoformat(),
            data=record.data,
            intervention=record.intervention,
            resolved_at=record.resolved_at.isoformat() if record.resolved_at else None,
            escalated=record.escalated
        )
        for record in pending
    ]


@app.get("/api/signals/{signal_id}")
async def get_signal(signal_id: str) -> SignalResponse:
    """
    Get details of a specific signal.
    """
    signal = mrp_engine.get_signal(signal_id)
    
    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Signal {signal_id} not found"
        )
    
    return SignalResponse(
        signal_id=signal.signal_id,
        status=signal.status.value,
        created_at=signal.created_at.isoformat(),
        data=signal.data,
        intervention=signal.intervention,
        resolved_at=signal.resolved_at.isoformat() if signal.resolved_at else None,
        escalated=signal.escalated
    )


@app.get("/api/signals")
async def get_all_signals() -> List[SignalResponse]:
    """
    Get all signals in the system.
    """
    signals = mrp_engine.get_all_signals()
    
    return [
        SignalResponse(
            signal_id=record.signal_id,
            status=record.status.value,
            created_at=record.created_at.isoformat(),
            data=record.data,
            intervention=record.intervention,
            resolved_at=record.resolved_at.isoformat() if record.resolved_at else None,
            escalated=record.escalated
        )
        for record in signals
    ]


@app.get("/api/audit/{signal_id}")
async def get_audit_trail(signal_id: str) -> List[AuditEntryResponse]:
    """
    Get the complete audit trail for a signal.
    """
    entries = audit_log.get_entries_for_signal(signal_id)
    
    if not entries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audit entries found for signal {signal_id}"
        )
    
    return [
        AuditEntryResponse(**entry)
        for entry in entries
    ]


@app.get("/api/audit")
async def get_audit_log(limit: Optional[int] = 100) -> List[AuditEntryResponse]:
    """
    Get recent audit log entries (limited for performance).
    """
    entries = audit_log.get_all_entries(limit=limit)
    
    return [
        AuditEntryResponse(**entry)
        for entry in entries
    ]


@app.get("/api/audit/statistics")
async def get_audit_statistics() -> Dict:
    """
    Get audit log statistics and verify chain integrity.
    """
    return audit_log.get_statistics()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
