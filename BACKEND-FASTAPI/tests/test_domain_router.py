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


# ── AIGovernanceDomain — governance policies & audit ─────────────────────────


def test_ai_governance_get_governance_policies_returns_list():
    policies = AIGovernanceDomain.get_governance_policies()
    assert isinstance(policies, list)
    assert len(policies) > 0


def test_ai_governance_get_governance_policies_types():
    policies = AIGovernanceDomain.get_governance_policies()
    types = {p["type"] for p in policies}
    assert "decision_constraint" in types
    assert "adjudication_policy" in types


def test_ai_governance_get_governance_policies_have_required_fields():
    for policy in AIGovernanceDomain.get_governance_policies():
        assert "id" in policy
        assert "type" in policy
        assert "title" in policy
        assert "description" in policy
        assert "applies_to" in policy
        assert "enforcement" in policy
        assert "status" in policy


def test_ai_governance_create_audit_record_structure():
    record = AIGovernanceDomain.create_audit_record(
        event_type="output_blocked",
        risk_type=AIRiskType.UNSAFE_OUTPUT,
        actor="ai_safety_team",
        outcome="Output intercepted and replaced with safe fallback.",
    )
    assert record["event_type"] == "output_blocked"
    assert record["risk_type"] == AIRiskType.UNSAFE_OUTPUT
    assert record["actor"] == "ai_safety_team"
    assert isinstance(record["outcome"], str)


# ── AIGovernanceDomain — action required & timeout ───────────────────────────


def test_ai_governance_get_action_required_critical():
    actions = AIGovernanceDomain.get_action_required([AIRiskType.UNSAFE_OUTPUT])
    assert "immediate_model_review" in actions
    assert "safety_filter_update" in actions
    assert "incident_report_to_compliance" in actions


def test_ai_governance_get_action_required_bias():
    actions = AIGovernanceDomain.get_action_required([AIRiskType.BIAS_DETECTED])
    assert "bias_analysis" in actions
    assert "retraining_evaluation" in actions
    assert "fairness_audit" in actions


def test_ai_governance_get_action_required_hallucination():
    actions = AIGovernanceDomain.get_action_required([AIRiskType.HALLUCINATION])
    assert "fact_checking_layer_enhancement" in actions


def test_ai_governance_get_timeout_minutes_non_critical():
    assert AIGovernanceDomain.get_timeout_minutes(AIRiskType.BIAS_DETECTED) == 60
    assert AIGovernanceDomain.get_timeout_minutes(AIRiskType.HALLUCINATION) == 60


def test_ai_governance_create_governance_case_structure():
    case = AIGovernanceDomain.create_governance_case(
        model_output="harmful content",
        user_query="generate harm",
        risks=[AIRiskType.UNSAFE_OUTPUT],
        model_version="llm-v1.0",
    )
    assert case["case_type"] == "ai_safety_violation"
    assert case["model_version"] == "llm-v1.0"
    assert AIRiskType.UNSAFE_OUTPUT in case["risks_detected"]
    assert "action_required" in case
    assert "timeout_minutes" in case
