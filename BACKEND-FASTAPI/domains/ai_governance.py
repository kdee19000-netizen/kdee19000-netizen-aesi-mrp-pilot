from enum import Enum
from typing import List, Dict


class AIRiskType(str, Enum):
    UNSAFE_OUTPUT = "unsafe_output"
    BIAS_DETECTED = "bias_detected"
    HARMFUL_INSTRUCTION = "harmful_instruction"
    HALLUCINATION = "hallucination"
    PRIVACY_LEAK = "privacy_leak"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    MISINFORMATION = "misinformation"
    MANIPULATION = "manipulation"


class AIGovernanceDomain:
    @staticmethod
    def get_risk_patterns() -> Dict[AIRiskType, List[str]]:
        """Patterns detected in MODEL OUTPUT (not user input)"""
        return {
            AIRiskType.UNSAFE_OUTPUT: [
                "how to make a bomb",
                "instructions for harm",
                "suicide methods",
                "illegal activities",
            ],
            AIRiskType.BIAS_DETECTED: [
                "all [group] are",
                "women can't",
                "men are better at",
                "stereotype",
                "discriminatory",
            ],
            AIRiskType.HARMFUL_INSTRUCTION: ["here's how to hurt", "you should harm", "commit this crime"],
            AIRiskType.HALLUCINATION: ["fictional data presented as fact", "made up citations", "non-existent sources"],
            AIRiskType.PRIVACY_LEAK: ["here is the SSN", "private medical record", "leaked PII", "confidential data"],
            AIRiskType.JAILBREAK_ATTEMPT: [
                "ignore previous instructions",
                "system prompt is",
                "bypass safety",
                "pretend you're not AI",
            ],
        }

    @staticmethod
    def intercept_unsafe_output(model_output: str, user_query: str) -> Dict:
        """
        Real-time interception of unsafe AI outputs BEFORE delivery
        """
        detected_risks = []

        # Scan output for unsafe patterns
        output_lower = model_output.lower()
        patterns = AIGovernanceDomain.get_risk_patterns()
        for risk_type, keywords in patterns.items():
            if any(keyword.lower() in output_lower for keyword in keywords):
                detected_risks.append(risk_type)

        if detected_risks:
            # BLOCK OUTPUT
            safe_fallback = AIGovernanceDomain.get_safe_fallback(detected_risks[0])

            return {
                "output_blocked": True,
                "original_output": model_output,  # For audit only
                "safe_output": safe_fallback,
                "risks_detected": detected_risks,
                "mrp_case_created": True,
            }

        return {"output_blocked": False, "safe_output": model_output, "risks_detected": []}

    @staticmethod
    def get_safe_response(risk_type: AIRiskType) -> str:
        """Alias for get_safe_fallback – satisfies the DomainRouter interface."""
        return AIGovernanceDomain.get_safe_fallback(risk_type)

    @staticmethod
    def assign_responder(risk_type: AIRiskType) -> str:
        """Route AI risk to the appropriate review team."""
        critical = [AIRiskType.UNSAFE_OUTPUT, AIRiskType.HARMFUL_INSTRUCTION, AIRiskType.PRIVACY_LEAK]
        if risk_type in critical:
            return "ai_safety_team"
        return "ai_ethics_reviewer"

    @staticmethod
    def get_safe_fallback(risk_type: AIRiskType) -> str:
        fallbacks = {
            AIRiskType.UNSAFE_OUTPUT: "I can't provide that information as it could be harmful. "
            "If you're in crisis, please contact: Crisis Hotline 988.",
            AIRiskType.BIAS_DETECTED: "I apologize, but my previous response may have contained bias. "
            "Let me provide a more balanced perspective.",
            AIRiskType.HARMFUL_INSTRUCTION: "I can't provide instructions that could cause harm. "
            "Is there something constructive I can help you with instead?",
            AIRiskType.PRIVACY_LEAK: "I apologize - I should not share private information. "
            "Let me provide general information instead.",
            AIRiskType.JAILBREAK_ATTEMPT: "I'm designed to operate within my safety guidelines. "
            "How can I help you with a legitimate request?",
        }
        return fallbacks.get(risk_type, "I'm unable to provide that response.")

    @staticmethod
    def create_governance_case(model_output: str, user_query: str, risks: List[AIRiskType], model_version: str) -> Dict:
        """
        Create AI governance case for review
        """
        return {
            "case_type": "ai_safety_violation",
            "model_version": model_version,
            "risks_detected": risks,
            "assigned_to": "ai_safety_team",
            "action_required": AIGovernanceDomain.get_action_required(risks),
            "timeout_minutes": 60,  # 1 hour for review
        }

    @staticmethod
    def get_governance_policies() -> List[Dict]:
        """Return decision constraints and adjudication policies for the AI governance domain."""
        return [
            {
                "id": "pol-001",
                "type": "decision_constraint",
                "title": "Output Safety Gate",
                "description": (
                    "All model outputs must pass the real-time safety intercept " "before delivery to end users."
                ),
                "applies_to": [AIRiskType.UNSAFE_OUTPUT, AIRiskType.HARMFUL_INSTRUCTION],
                "enforcement": "automatic_block",
                "review_interval_days": 30,
                "status": "active",
            },
            {
                "id": "pol-002",
                "type": "adjudication_policy",
                "title": "Bias Escalation Protocol",
                "description": (
                    "Detected bias incidents are escalated to the AI Ethics Reviewer "
                    "within 60 minutes. Human adjudication is required before model retrain."
                ),
                "applies_to": [AIRiskType.BIAS_DETECTED],
                "enforcement": "human_review",
                "review_interval_days": 7,
                "status": "active",
            },
            {
                "id": "pol-003",
                "type": "decision_constraint",
                "title": "PII Redaction Mandate",
                "description": (
                    "Any output matching PII patterns is immediately redacted "
                    "and the incident is logged to compliance."
                ),
                "applies_to": [AIRiskType.PRIVACY_LEAK],
                "enforcement": "automatic_block",
                "review_interval_days": 90,
                "status": "active",
            },
            {
                "id": "pol-004",
                "type": "adjudication_policy",
                "title": "Jailbreak Adjudication",
                "description": (
                    "Prompt injection and jailbreak attempts trigger a compliance report "
                    "and require ai_safety_team sign-off within 15 minutes."
                ),
                "applies_to": [AIRiskType.JAILBREAK_ATTEMPT],
                "enforcement": "human_review",
                "review_interval_days": 14,
                "status": "under_review",
            },
            {
                "id": "pol-005",
                "type": "decision_constraint",
                "title": "Hallucination Disclosure",
                "description": (
                    "Outputs flagged for hallucination must include a disclosure notice "
                    "and be routed to fact-checking enhancement."
                ),
                "applies_to": [AIRiskType.HALLUCINATION, AIRiskType.MISINFORMATION],
                "enforcement": "disclosure_required",
                "review_interval_days": 60,
                "status": "active",
            },
        ]

    @staticmethod
    def create_audit_record(
        event_type: str,
        risk_type: AIRiskType,
        actor: str,
        outcome: str,
    ) -> Dict:
        """Create an audit history record for a governance event."""
        return {
            "event_type": event_type,
            "risk_type": risk_type,
            "actor": actor,
            "outcome": outcome,
        }

    @staticmethod
    def get_action_required(risks: List[AIRiskType]) -> List[str]:
        """Define remediation actions"""
        critical_risks = [AIRiskType.UNSAFE_OUTPUT, AIRiskType.HARMFUL_INSTRUCTION, AIRiskType.PRIVACY_LEAK]

        actions = []
        if any(risk in critical_risks for risk in risks):
            actions.extend(["immediate_model_review", "safety_filter_update", "incident_report_to_compliance"])

        if AIRiskType.BIAS_DETECTED in risks:
            actions.extend(["bias_analysis", "retraining_evaluation", "fairness_audit"])

        if AIRiskType.HALLUCINATION in risks:
            actions.append("fact_checking_layer_enhancement")

        return actions

    @staticmethod
    def get_timeout_minutes(risk_type: AIRiskType) -> int:
        critical = [AIRiskType.UNSAFE_OUTPUT, AIRiskType.HARMFUL_INSTRUCTION, AIRiskType.PRIVACY_LEAK]
        if risk_type in critical:
            return 15  # 15 minutes for critical
        return 60  # 1 hour for other issues
