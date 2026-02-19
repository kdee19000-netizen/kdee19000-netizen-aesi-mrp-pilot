"""AuditLog ORM model – immutable append-only records."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # IMMUTABILITY CRITICAL FIELDS
    id = Column(String, primary_key=True)
    record_id = Column(String, ForeignKey("risk_records.id"), nullable=False)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    event_hash = Column(String, nullable=False, unique=True)
    prev_hash = Column(String, nullable=True)

    # Quantum-Resistant Signatures
    signature = Column(Text, nullable=False)
    pq_algorithm = Column(String, default="dilithium3")
    classical_algorithm = Column(String, default="rsa4096")

    # Block Chain Info
    block_number = Column(Integer, nullable=True)
    merkle_root = Column(String, nullable=True)

    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    evidence_note = Column(Text, nullable=True)
    audit_version = Column(String, default="2.0")

    # Relationships
    record = relationship("RiskRecord", back_populates="audit_logs")
