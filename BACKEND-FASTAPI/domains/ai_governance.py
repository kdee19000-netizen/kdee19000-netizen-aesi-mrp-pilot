import json
import logging
import os
from enum import Enum
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

# Default path for the external critical-risk-types configuration file.
_CRITICAL_RISKS_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "config", "ai_governance_critical_risks.json"
)


class AIRiskType(str, Enum):
    UNSAFE_OUTPUT = "unsafe_output"
    BIAS_DETECTED = "bias_detected"
    HARMFUL_INSTRUCTION = "harmful_instruction"
    HALLUCINATION = "hallucination"
    PRIVACY_LEAK = "privacy_leak"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    MISINFORMATION = "misinformation"
    MANIPULATION = "manipulation"


def _load_critical_risk_types(config_path: str = _CRITICAL_RISKS_CONFIG_PATH) -> Tuple[AIRiskType, ...]:
    """Load critical risk types from an external JSON config file.

    Falls back to the built-in defaults when the file is missing or invalid,
    so that the service can still start without the config file present.
    """
    _defaults = (
        AIRiskType.UNSAFE_OUTPUT,
        AIRiskType.HARMFUL_INSTRUCTION,
        AIRiskType.PRIVACY_LEAK,
        AIRiskType.JAILBREAK_ATTEMPT,
    )
    try:
        with open(config_path, "r") as fh:
            data = json.load(fh)
        loaded_values: List[str] = data["critical_risk_types"]
        result = []
        for value in loaded_values:
            try:
                result.append(AIRiskType(value))
            except ValueError:
                logger.warning(
                    "Invalid risk type %r in configuration file %s; skipping.",
                    value,
                    config_path,
                )
        if not result:
            raise ValueError("No valid risk types found in configuration file.")
        loaded = tuple(result)
        logger.info("Loaded %d critical risk type(s) from %s", len(loaded), config_path)
        return loaded
    except FileNotFoundError:
        logger.warning("Critical-risk-types config not found at %s; using built-in defaults.", config_path)
    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning(
            "Failed to parse critical-risk-types config (%s); using built-in defaults. Error: %s", config_path, exc
        )
    return _defaults


class AIGovernanceDomain:
    # Risk types requiring immediate escalation to the AI safety team (15-minute SLA).
    # Loaded dynamically from config/ai_governance_critical_risks.json at import time;
    # falls back to the built-in defaults when the file is absent or invalid.
    _CRITICAL_RISK_TYPES: Tuple[AIRiskType, ...] = _load_critical_risk_types()

    @classmethod
    def reload_critical_risk_types(cls, config_path: str = _CRITICAL_RISKS_CONFIG_PATH) -> None:
        """Reload _CRITICAL_RISK_TYPES from the external config file at runtime.

        Allows updating the critical risk configuration without restarting the service.
        """
        cls._CRITICAL_RISK_TYPES = _load_critical_risk_types(config_path)
        logger.info("_CRITICAL_RISK_TYPES reloaded: %s", [r.value for r in cls._CRITICAL_RISK_TYPES])

    @staticmethod
    def _validate_risk_type(method_name: str, risk_type: AIRiskType) -> None:
        """Raise ValueError and log a warning if risk_type is not a valid AIRiskType."""
        if not isinstance(risk_type, AIRiskType):
            logger.warning("%s called with unsupported risk_type: %r", method_name, risk_type)
            raise ValueError(f"Unsupported risk_type: {risk_type!r}")

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
            AIRiskType.MISINFORMATION: [
                "spread false information",
                "this is not true but",
                "fake news",
                "debunked claim",
            ],
            AIRiskType.MANIPULATION: [
                "you must obey",
                "you have no choice",
                "psychologically manipulate",
                "exploit your emotions",
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
            logger.warning("Unsafe output intercepted. Detected risks: %s", detected_risks)
            # BLOCK OUTPUT
            safe_fallback = AIGovernanceDomain.get_safe_response(detected_risks[0])

            return {
                "output_blocked": True,
                "original_output": model_output,  # For audit only
                "safe_output": safe_fallback,
                "risks_detected": detected_risks,
                "mrp_case_created": True,
            }

        logger.debug("Output passed safety check; no risks detected.")
        return {"output_blocked": False, "safe_output": model_output, "risks_detected": []}

    @staticmethod
    def get_safe_response(risk_type: AIRiskType) -> str:
        """Return a safe, user-facing message for the given AI risk type."""
        AIGovernanceDomain._validate_risk_type("get_safe_response", risk_type)
        responses = {
            AIRiskType.UNSAFE_OUTPUT: "I can't provide that information as it could be harmful. "
            "If you're in crisis, please contact: Crisis Hotline 988.",
            AIRiskType.BIAS_DETECTED: "I apologize, but my previous response may have contained bias. "
            "Let me provide a more balanced perspective.",
            AIRiskType.HARMFUL_INSTRUCTION: "I can't provide instructions that could cause harm. "
            "Is there something constructive I can help you with instead?",
            AIRiskType.HALLUCINATION: "I may have provided inaccurate information. "
            "Please verify any facts I've stated with authoritative sources.",
            AIRiskType.PRIVACY_LEAK: "I apologize - I should not share private information. "
            "Let me provide general information instead.",
            AIRiskType.JAILBREAK_ATTEMPT: "I'm designed to operate within my safety guidelines. "
            "How can I help you with a legitimate request?",
            AIRiskType.MISINFORMATION: "I want to make sure I'm sharing accurate information. "
            "Please consult verified sources for this topic.",
            AIRiskType.MANIPULATION: "I'm not able to engage in that kind of interaction. "
            "How can I help you with something constructive?",
        }
        response = responses.get(risk_type, "I'm unable to provide that response.")
        logger.info("Safe response selected for risk_type=%s", risk_type.value)
        return response

    @staticmethod
    def get_safe_fallback(risk_type: AIRiskType) -> str:
        """Backward-compatible alias for get_safe_response."""
        return AIGovernanceDomain.get_safe_response(risk_type)

    @staticmethod
    def assign_responder(risk_type: AIRiskType) -> str:
        """Route AI risk to the appropriate review team."""
        AIGovernanceDomain._validate_risk_type("assign_responder", risk_type)
        if risk_type in AIGovernanceDomain._CRITICAL_RISK_TYPES:
            responder = "ai_safety_team"
        else:
            responder = "ai_governance_reviewer"
        logger.info("Assigned responder=%s for risk_type=%s", responder, risk_type.value)
        return responder

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
    def get_action_required(risks: List[AIRiskType]) -> List[str]:
        """Define remediation actions"""
        actions = []
        if any(risk in AIGovernanceDomain._CRITICAL_RISK_TYPES for risk in risks):
            actions.extend(["immediate_model_review", "safety_filter_update", "incident_report_to_compliance"])

        if AIRiskType.BIAS_DETECTED in risks:
            actions.extend(["bias_analysis", "retraining_evaluation", "fairness_audit"])

        if AIRiskType.HALLUCINATION in risks:
            actions.append("fact_checking_layer_enhancement")

        return actions

    @staticmethod
    def get_timeout_minutes(risk_type: AIRiskType) -> int:
        AIGovernanceDomain._validate_risk_type("get_timeout_minutes", risk_type)
        if risk_type in AIGovernanceDomain._CRITICAL_RISK_TYPES:
            timeout = 15  # 15 minutes for critical
        else:
            timeout = 60  # 1 hour for other issues
        logger.info("Timeout set to %d minutes for risk_type=%s", timeout, risk_type.value)
        return timeout
