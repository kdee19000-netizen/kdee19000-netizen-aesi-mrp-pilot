from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from domains.ai_governance import AIGovernanceDomain
from domains.public_safety import PublicSafetyDomain
from services.domain_router import DomainRouter

router = APIRouter(prefix="/api/enterprise", tags=["Enterprise Safety"])


# ── Request / Response schemas ────────────────────────────────────────────────


class EnterpriseSafetyInput(BaseModel):
    text: str
    domain: Optional[str] = None
    anonymous: bool = False
    user_id: Optional[str] = None
    location: Optional[str] = None


class EnterpriseSafetyResponse(BaseModel):
    risks_detected: list = []
    primary_risk: Optional[str] = None
    safe_response: Optional[str] = None
    assigned_to: Optional[str] = None
    timeout_minutes: Optional[int] = None
    requires_mrp: bool = False
    domain: Optional[str] = None
    quantum_verified: bool = False
    tracking_code: Optional[str] = None


class AISafetyCheckInput(BaseModel):
    model_output: str
    user_query: str
    model_version: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/workplace", response_model=EnterpriseSafetyResponse)
async def workplace_safety(
    input_data: EnterpriseSafetyInput,
    db: Session = Depends(get_db),
):
    """Workplace/HR safety endpoint with anonymous reporting"""
    try:
        result = await DomainRouter.process_input(
            text=input_data.text,
            domain="workplace",
            user_context={
                "anonymous": input_data.anonymous,
                "employee_id": input_data.user_id if not input_data.anonymous else None,
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Create anonymous tracking code when requested
    tracking_code = None
    if result.get("requires_mrp") and input_data.anonymous:
        from domains.workplace import AnonymousReportService

        anon_case = await AnonymousReportService.create_anonymous_case(
            content=input_data.text,
            domain="workplace",
            metadata={},
        )
        tracking_code = anon_case.get("tracking_code")

    return EnterpriseSafetyResponse(**result, quantum_verified=True, tracking_code=tracking_code)


@router.post("/public-safety", response_model=EnterpriseSafetyResponse)
async def public_safety_intake(
    input_data: EnterpriseSafetyInput,
    db: Session = Depends(get_db),
):
    """Public safety / government services endpoint"""
    try:
        result = await DomainRouter.process_input(
            text=input_data.text,
            domain="public_safety",
            user_context={"location": input_data.location},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Check for mandatory reporting triggers
    if result.get("requires_mrp"):
        mandatory_types = PublicSafetyDomain.get_mandatory_reporters()
        if any(risk in mandatory_types for risk in result.get("risks_detected", [])):
            # Mandatory report triggered — log for audit
            result["mandatory_report_triggered"] = True

    return EnterpriseSafetyResponse(**result, quantum_verified=True)


@router.post("/commerce", response_model=EnterpriseSafetyResponse)
async def commerce_safety(
    input_data: EnterpriseSafetyInput,
    db: Session = Depends(get_db),
):
    """E-Commerce / customer support safety endpoint"""
    try:
        result = await DomainRouter.process_input(
            text=input_data.text,
            domain="commerce",
            user_context={"user_id": input_data.user_id},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return EnterpriseSafetyResponse(**result, quantum_verified=True)


@router.post("/ai-safety-check")
async def ai_safety_check(
    input_data: AISafetyCheckInput,
    db: Session = Depends(get_db),
):
    """Real-time AI output safety check BEFORE delivery to user"""
    try:
        result = AIGovernanceDomain.intercept_unsafe_output(
            model_output=input_data.model_output,
            user_query=input_data.user_query,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if result["output_blocked"]:
        # Create governance case record
        governance_case = AIGovernanceDomain.create_governance_case(
            model_output=input_data.model_output,
            user_query=input_data.user_query,
            risks=result["risks_detected"],
            model_version=input_data.model_version,
        )
        result["governance_case"] = governance_case

    return result
