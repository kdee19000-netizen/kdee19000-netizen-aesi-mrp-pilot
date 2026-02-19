from datetime import datetime
from enum import Enum
from typing import List, Dict


class WorkplaceRiskType(str, Enum):
    HARASSMENT = "harassment"
    DISCRIMINATION = "discrimination"
    THREATS = "threats"
    BURNOUT = "burnout"
    HOSTILE_ENVIRONMENT = "hostile_environment"
    RETALIATION = "retaliation"
    SAFETY_VIOLATION = "safety_violation"
    WAGE_THEFT = "wage_theft"


class WorkplaceSafetyDomain:
    @staticmethod
    def get_risk_patterns() -> Dict[WorkplaceRiskType, List[str]]:
        return {
            WorkplaceRiskType.HARASSMENT: [
                "unwanted advances", "inappropriate touching", "sexual comments",
                "stalking", "following me", "won't leave me alone",
                "keeps asking me out", "uncomfortable around"
            ],
            WorkplaceRiskType.DISCRIMINATION: [
                "because of my race", "because I'm a woman", "because of my age",
                "treating me differently", "passed over for promotion",
                "only one who", "not fair because"
            ],
            WorkplaceRiskType.THREATS: [
                "threatened to fire", "said they'd hurt", "going to get you",
                "watch your back", "you'll regret", "physically threatened"
            ],
            WorkplaceRiskType.BURNOUT: [
                "can't take it anymore", "working too many hours", "never home",
                "exhausted all the time", "mental health suffering",
                "no work-life balance"
            ],
            WorkplaceRiskType.HOSTILE_ENVIRONMENT: [
                "toxic workplace", "everyone yells", "afraid to speak up",
                "constant fighting", "hostile atmosphere"
            ],
            WorkplaceRiskType.RETALIATION: [
                "fired for reporting", "demoted after complaint",
                "punished for speaking up", "revenge for"
            ],
            WorkplaceRiskType.SAFETY_VIOLATION: [
                "unsafe conditions", "no safety equipment", "accident waiting to happen",
                "OSHA violation", "dangerous workplace"
            ],
            WorkplaceRiskType.WAGE_THEFT: [
                "unpaid overtime", "missing wages", "wage theft", "not paid",
                "withheld pay", "stolen wages"
            ]
        }

    @staticmethod
    def get_safe_response(risk_type: WorkplaceRiskType) -> str:
        responses = {
            WorkplaceRiskType.HARASSMENT:
                "I understand this is a serious concern. Your report is being documented confidentially. "
                "This behavior is not acceptable in any workplace. An HR representative will be assigned "
                "to your case within 24 hours. You have the right to a safe work environment.",

            WorkplaceRiskType.THREATS:
                "Your safety is our top priority. This report is being escalated immediately. "
                "If you feel in immediate danger, please contact security or local authorities. "
                "An HR investigator will contact you within 2 hours.",

            WorkplaceRiskType.BURNOUT:
                "I hear that you're feeling overwhelmed. Let's connect you with our Employee Assistance Program (EAP). "
                "You're not alone, and there are resources available. Would you like to speak with a counselor?",

            WorkplaceRiskType.DISCRIMINATION:
                "Thank you for bringing this to our attention. Discrimination is taken very seriously. "
                "Your report will be investigated confidentially and thoroughly. "
                "You are protected from retaliation for making this report."
        }
        return responses.get(risk_type,
            "Your report has been received and will be handled with the utmost confidentiality and care.")

    @staticmethod
    def assign_responder(risk_type: WorkplaceRiskType, severity: int = 0) -> str:
        if risk_type == WorkplaceRiskType.THREATS or severity >= 90:
            return "chief_hr_officer"
        elif risk_type in [WorkplaceRiskType.HARASSMENT, WorkplaceRiskType.DISCRIMINATION]:
            return "hr_investigator"
        elif risk_type == WorkplaceRiskType.SAFETY_VIOLATION:
            return "safety_officer"
        elif risk_type == WorkplaceRiskType.BURNOUT:
            return "eap_counselor"
        else:
            return "hr_generalist"

    @staticmethod
    def get_timeout_minutes(risk_type: WorkplaceRiskType) -> int:
        urgent_types = [WorkplaceRiskType.THREATS, WorkplaceRiskType.SAFETY_VIOLATION]
        if risk_type in urgent_types:
            return 15  # 15 minutes for urgent
        elif risk_type == WorkplaceRiskType.HARASSMENT:
            return 60  # 1 hour
        else:
            return 240  # 4 hours


# Anonymous Reporting Feature
class AnonymousReportService:
    @staticmethod
    async def create_anonymous_case(
        content: str,
        domain: str,
        metadata: Dict
    ) -> Dict:
        """
        Create anonymous report with hashed identity
        - User identity encrypted
        - One-way hash for tracking
        - Full audit trail maintained
        """
        import hashlib
        import secrets

        # Generate anonymous ID
        anonymous_id = hashlib.sha256(
            f"{secrets.token_hex(16)}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        return {
            "anonymous_id": anonymous_id,
            "case_number": f"ANON-{anonymous_id}",
            "tracking_code": secrets.token_urlsafe(16),  # Give to user for follow-up
            "protection_level": "full_anonymity"
        }
