"""Pydantic schemas for audit log responses."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: str
    record_id: str
    action: str
    actor: str
    timestamp: datetime
    event_hash: str
    prev_hash: Optional[str]
    signature: str
    pq_algorithm: str
    classical_algorithm: str
    block_number: Optional[int]
    evidence_note: Optional[str]
    audit_version: str

    model_config = {"from_attributes": True}


class AuditProofResponse(BaseModel):
    valid: bool
    entries: Optional[int] = None
    reason: Optional[str] = None
    log_id: Optional[str] = None
    quantum_safe: bool = True
