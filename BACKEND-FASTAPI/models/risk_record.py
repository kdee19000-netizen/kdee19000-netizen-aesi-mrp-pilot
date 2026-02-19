"""RiskRecord ORM model."""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class RiskStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class RiskRecord(Base):
    __tablename__ = "risk_records"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    parent_id = Column(String, nullable=True, index=True)
    content_hash = Column(String, unique=True)
    content_encrypted = Column(Text)
    metadata_json = Column(JSON)
    risk_score = Column(Integer, default=0)
    status = Column(SQLEnum(RiskStatus), default=RiskStatus.PENDING)
    assigned_to = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    verified_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    language = Column(String, nullable=True)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="record")
