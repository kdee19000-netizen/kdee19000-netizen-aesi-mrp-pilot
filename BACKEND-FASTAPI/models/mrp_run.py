"""MRPRun ORM model – tracks each MRP calculation run."""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, Integer, String

from .base import Base


class MRPStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MRPRun(Base):
    __tablename__ = "mrp_runs"

    id = Column(String, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(MRPStatus), default=MRPStatus.QUEUED)
    items_processed = Column(Integer, default=0)
    planned_orders = Column(JSON)
    errors = Column(JSON)
    triggered_by = Column(String)
