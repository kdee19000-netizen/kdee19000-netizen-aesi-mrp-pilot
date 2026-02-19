"""
Audit Service

Appends immutable, quantum-signed entries to the audit chain and verifies
the integrity of the full chain for a given record.
"""

import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from models.audit_log import AuditLog
from services.quantum_crypto import crypto_service


class AuditService:
    @staticmethod
    def append_audit(
        db: Session,
        record_id: str,
        action: str,
        actor: str,
        evidence: str = None,
        ip_address: str = None,
    ) -> AuditLog:
        """Append an IMMUTABLE audit entry with quantum-hybrid signature."""
        # Fetch previous entry to build hash chain
        prev = (
            db.query(AuditLog)
            .filter(AuditLog.record_id == record_id)
            .order_by(AuditLog.timestamp.desc())
            .first()
        )
        prev_hash = prev.event_hash if prev else "genesis"

        # Build deterministic payload
        payload = (
            f"{action}|{actor}|{datetime.utcnow().isoformat()}"
            f"|{record_id}|{evidence or ''}|{prev_hash}"
        )
        event_hash = crypto_service.generate_hash(payload)
        signature = crypto_service.hybrid_sign(payload)

        # Verify before persisting
        if not crypto_service.verify_signature(payload, signature):
            raise ValueError("Signature verification failed before commit")

        audit = AuditLog(
            id=str(uuid.uuid4()),
            record_id=record_id,
            action=action,
            actor=actor,
            event_hash=event_hash,
            prev_hash=prev_hash,
            signature=signature,
            evidence_note=evidence,
            ip_address=ip_address,
        )

        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def verify_chain(db: Session, record_id: str) -> dict:
        """Verify the integrity of the full audit chain for *record_id*."""
        logs = (
            db.query(AuditLog)
            .filter(AuditLog.record_id == record_id)
            .order_by(AuditLog.timestamp)
            .all()
        )

        if not logs:
            return {"valid": False, "reason": "No audit logs found"}

        for i, log in enumerate(logs):
            expected_prev = logs[i - 1].event_hash if i > 0 else "genesis"
            if log.prev_hash != expected_prev:
                return {
                    "valid": False,
                    "reason": f"Chain broken at entry {i}",
                    "log_id": log.id,
                }

        return {"valid": True, "entries": len(logs)}
