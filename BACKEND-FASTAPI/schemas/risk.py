"""Pydantic schemas for risk signals and responses."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RiskSignal(BaseModel):
    user_id: str = Field(..., description="ID of the user raising the risk signal")
    content: str = Field(..., description="Raw content to be analysed for risk")
    parent_id: Optional[str] = Field(None, description="Parent/guardian user ID if applicable")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    language: Optional[str] = Field(None, description="ISO 639-1 language code (auto-detected if omitted)")


class RiskResponse(BaseModel):
    id: str
    user_id: str
    risk_score: int
    status: str
    content_hash: str
    created_at: datetime
    quantum_signed: bool = True
    mrp_timer_started: bool = False

    model_config = {"from_attributes": True}


class InterventionRequest(BaseModel):
    record_id: str = Field(..., description="ID of the risk record to act on")
    action: str = Field(..., description="Action taken: VERIFY, ESCALATE, RESOLVE, FALSE_POSITIVE")
    actor: str = Field(..., description="Username or ID of the responding staff member")
    evidence: Optional[str] = Field(None, description="Free-text evidence / notes")
    ip_address: Optional[str] = None
