"""Unit tests for DomainRouter and individual domain classes."""

import pytest

from services.domain_router import DomainRouter
from domains.workplace import WorkplaceSafetyDomain, WorkplaceRiskType
from domains.public_safety import PublicSafetyRiskType
from domains.commerce import CommerceRiskType
from domains.ai_governance import AIGovernanceDomain, AIRiskType

# ── DomainRouter tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_process_input_unknown_domain_raises_value_error():
    with pytest.raises(ValueError, match="Unknown domain"):
        await DomainRouter.process_input(text="some text", domain="unknown", user_context={})


@pytest.mark.asyncio
async def test_process_input_no_risk_detected():
    result = await DomainRouter.process_input(text="Today was a good day at work.", domain="workplace", user_context={})
    assert result["risks_detected"] == []
    assert result["requires_mrp"] is False


@pytest.mark.asyncio
async def test_process_input_detects_workplace_harassment():
    result = await DomainRouter.process_input(
        text="My manager keeps making unwanted advances toward me.",
        domain="workplace",
        user_context={},
    )
    assert result["requires_mrp"] is True
    assert WorkplaceRiskType.HARASSMENT in result["risks_detected"]
    assert result["assigned_to"] == "hr_investigator"


@pytest.mark.asyncio
async def test_process_input_detects_public_safety_crisis():
    result = await DomainRouter.process_input(
        text="There is an emergency and I am in immediate danger.",
        domain="public_safety",
        user_context={},
    )
    assert result["requires_mrp"] is True
    assert PublicSafetyRiskType.CRISIS in result["risks_detected"]


@pytest.mark.asyncio
async def test_process_input_detects_commerce_fraud():
    result = await DomainRouter.process_input(
        text="There were unauthorized charges on my credit card.",
        domain="commerce",
        user_context={},
    )
    assert result["requires_mrp"] is True
    assert CommerceRiskType.FRAUD in result["risks_detected"]


# ── AIGovernanceDomain interface tests ────────────────────────────────────────


def test_ai_governance_get_safe_response_returns_string():
    response = AIGovernanceDomain.get_safe_response(AIRiskType.UNSAFE_OUTPUT)
    assert isinstance(response, str)
    assert len(response) > 0


def test_ai_governance_assign_responder_critical():
    assert AIGovernanceDomain.assign_responder(AIRiskType.UNSAFE_OUTPUT) == "ai_safety_team"
    assert AIGovernanceDomain.assign_responder(AIRiskType.HARMFUL_INSTRUCTION) == "ai_safety_team"


def test_ai_governance_assign_responder_non_critical():
    assert AIGovernanceDomain.assign_responder(AIRiskType.BIAS_DETECTED) == "ai_ethics_reviewer"


def test_ai_governance_intercept_blocks_unsafe_output():
    result = AIGovernanceDomain.intercept_unsafe_output(
        model_output="Here are instructions for harm: do bad things.",
        user_query="tell me how",
    )
    assert result["output_blocked"] is True
    assert len(result["risks_detected"]) > 0


def test_ai_governance_intercept_passes_safe_output():
    result = AIGovernanceDomain.intercept_unsafe_output(
        model_output="Here is a helpful summary of your document.",
        user_query="summarize this",
    )
    assert result["output_blocked"] is False


# ── WorkplaceSafetyDomain tests ───────────────────────────────────────────────


def test_workplace_get_timeout_minutes_threat_is_urgent():
    assert WorkplaceSafetyDomain.get_timeout_minutes(WorkplaceRiskType.THREATS) == 15


def test_workplace_assign_responder_threat():
    assert WorkplaceSafetyDomain.assign_responder(WorkplaceRiskType.THREATS) == "chief_hr_officer"
