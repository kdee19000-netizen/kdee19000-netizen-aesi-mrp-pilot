"""
Risk Service

Handles creation of risk signals and staff interventions.
Starts the 10-minute MRP timer on risk creation.
"""

import hashlib
import uuid
from datetime import datetime

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from models.risk_record import RiskRecord, RiskStatus
from schemas.risk import InterventionRequest, RiskSignal
from services.audit_service import AuditService

try:
    from langdetect import detect as lang_detect  # type: ignore
except ImportError:
    lang_detect = None


def _detect_language(text: str) -> str:
    if lang_detect:
        try:
            return lang_detect(text)
        except Exception:
            pass
    return "en"


def _score_content(content: str) -> int:
    """Simple heuristic risk scorer (0-100). Replace with ML model."""
    keywords = ["urgent", "danger", "crisis", "help", "emergency"]
    score = sum(10 for kw in keywords if kw.lower() in content.lower())
    return min(score, 100)


class RiskService:
    @staticmethod
    async def create_signal(
        db: Session,
        signal: RiskSignal,
        background_tasks: BackgroundTasks,
    ) -> RiskRecord:
        content_hash = hashlib.sha512(signal.content.encode()).hexdigest()

        # Idempotency – return existing record if hash already seen
        existing = db.query(RiskRecord).filter(RiskRecord.content_hash == content_hash).first()
        if existing:
            return existing

        risk_score = _score_content(signal.content)
        language = signal.language or _detect_language(signal.content)

        record = RiskRecord(
            id=str(uuid.uuid4()),
            user_id=signal.user_id,
            parent_id=signal.parent_id,
            content_hash=content_hash,
            content_encrypted=signal.content,  # Encrypt with KMS in production
            metadata_json=signal.metadata or {},
            risk_score=risk_score,
            status=RiskStatus.PENDING,
            language=language,
            created_at=datetime.utcnow(),
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Immutable audit entry
        AuditService.append_audit(
            db,
            record_id=record.id,
            action="SIGNAL_CREATED",
            actor=signal.user_id,
        )

        # Schedule 10-minute MRP timer in background
        background_tasks.add_task(_mrp_timer_task, record.id)

        return record

    @staticmethod
    async def handle_intervention(
        db: Session,
        intervention: InterventionRequest,
    ) -> dict:
        record = db.query(RiskRecord).filter(RiskRecord.id == intervention.record_id).first()
        if not record:
            from fastapi import HTTPException

            raise HTTPException(status_code=404, detail="Risk record not found")

        action = intervention.action.upper()
        now = datetime.utcnow()

        if action == "VERIFY":
            record.status = RiskStatus.VERIFIED
            record.verified_at = now
        elif action == "ESCALATE":
            record.status = RiskStatus.ESCALATED
            record.escalated_at = now
        elif action == "RESOLVE":
            record.status = RiskStatus.RESOLVED
            record.resolved_at = now
        elif action == "FALSE_POSITIVE":
            record.status = RiskStatus.FALSE_POSITIVE
            record.resolved_at = now
        else:
            from fastapi import HTTPException

            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

        record.assigned_to = intervention.actor
        db.commit()
        db.refresh(record)

        AuditService.append_audit(
            db,
            record_id=record.id,
            action=action,
            actor=intervention.actor,
            evidence=intervention.evidence,
            ip_address=intervention.ip_address,
        )

        return {"record_id": record.id, "new_status": record.status, "actor": intervention.actor}


async def _mrp_timer_task(record_id: str):
    """Placeholder for the 10-minute MRP timer background task."""
    import asyncio
    import logging
    import os

    logger = logging.getLogger(__name__)
    timer_seconds = int(os.getenv("MRP_TIMER_SECONDS", "600"))
    logger.info("MRP timer started: record_id=%s seconds=%d", record_id, timer_seconds)
    await asyncio.sleep(timer_seconds)
    logger.info("MRP timer expired: record_id=%s – triggering MRP run", record_id)
    # In production: trigger MRP recalculation via Celery/Redis
