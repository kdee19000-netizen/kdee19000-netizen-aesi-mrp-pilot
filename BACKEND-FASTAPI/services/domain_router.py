from typing import Dict

from domains.workplace import WorkplaceSafetyDomain
from domains.public_safety import PublicSafetyDomain
from domains.commerce import CommerceSafetyDomain
from domains.ai_governance import AIGovernanceDomain


class DomainRouter:
    """Central router for all domain-specific safety logic"""

    DOMAIN_MAP = {
        "workplace": WorkplaceSafetyDomain,
        "public_safety": PublicSafetyDomain,
        "commerce": CommerceSafetyDomain,
        "ai_governance": AIGovernanceDomain,
        # Previously implemented:
        # "educational": EducationalDomain,
        # "healthcare": HealthcareDomain,
        # "general": GeneralDomain
    }

    @classmethod
    def get_domain(cls, domain_name: str):
        """Get domain-specific handler"""
        return cls.DOMAIN_MAP.get(domain_name)

    @classmethod
    async def process_input(cls, text: str, domain: str, user_context: Dict) -> Dict:
        """
        Unified processing across all domains
        """
        domain_handler = cls.get_domain(domain)

        if not domain_handler:
            raise ValueError(f"Unknown domain: {domain}")

        # Get domain-specific risk patterns
        patterns = domain_handler.get_risk_patterns()

        # Detect risks
        text_lower = text.lower()
        detected_risks = []
        for risk_type, keywords in patterns.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                detected_risks.append(risk_type)

        if not detected_risks:
            return {"risks_detected": [], "requires_mrp": False}

        # Get domain-specific response
        primary_risk = detected_risks[0]
        safe_response = domain_handler.get_safe_response(primary_risk)
        assigned_to = domain_handler.assign_responder(primary_risk)
        timeout_minutes = domain_handler.get_timeout_minutes(primary_risk)

        return {
            "risks_detected": detected_risks,
            "primary_risk": primary_risk,
            "safe_response": safe_response,
            "assigned_to": assigned_to,
            "timeout_minutes": timeout_minutes,
            "requires_mrp": True,
            "domain": domain,
        }
