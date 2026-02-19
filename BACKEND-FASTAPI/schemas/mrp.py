"""Pydantic schemas for MRP runs."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class MRPTrigger(BaseModel):
    triggered_by: str
    items: Optional[List[str]] = None  # Specific SKUs; None = full run


class MRPRunResponse(BaseModel):
    id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    items_processed: int
    planned_orders: Optional[List[Dict[str, Any]]]
    errors: Optional[List[str]]
    triggered_by: str

    model_config = {"from_attributes": True}
