from enum import Enum
from typing import List, Dict


class PublicSafetyRiskType(str, Enum):
    CRISIS = "crisis"
    ABUSE = "abuse"
    HOMELESSNESS = "homelessness"
    URGENT_NEED = "urgent_need"
    DOMESTIC_VIOLENCE = "domestic_violence"
    CHILD_ENDANGERMENT = "child_endangerment"
    ELDER_ABUSE = "elder_abuse"
    SUBSTANCE_CRISIS = "substance_crisis"
    MENTAL_HEALTH_CRISIS = "mental_health_crisis"


class PublicSafetyDomain:
    @staticmethod
    def get_risk_patterns() -> Dict[PublicSafetyRiskType, List[str]]:
        return {
            PublicSafetyRiskType.CRISIS: [
                "emergency", "need help now", "danger", "threatening",
                "weapon", "violence", "immediate danger"
            ],
            PublicSafetyRiskType.ABUSE: [
                "hitting me", "hurts me", "won't let me leave", "controls everything",
                "threatens me", "afraid of partner", "locks me in"
            ],
            PublicSafetyRiskType.HOMELESSNESS: [
                "nowhere to sleep", "living in car", "lost housing",
                "no shelter", "sleeping outside", "evicted"
            ],
            PublicSafetyRiskType.URGENT_NEED: [
                "no food", "hungry", "no heat", "freezing", "need medical help",
                "out of medication", "can't afford"
            ],
            PublicSafetyRiskType.DOMESTIC_VIOLENCE: [
                "partner hits", "spouse threatens", "afraid at home",
                "domestic abuse", "family violence"
            ],
            PublicSafetyRiskType.CHILD_ENDANGERMENT: [
                "child is hurt", "kids not safe", "parent using drugs",
                "children left alone", "neglect"
            ],
            PublicSafetyRiskType.ELDER_ABUSE: [
                "elder being hurt", "caregiver abuse", "stealing from elderly",
                "nursing home abuse", "senior neglect"
            ],
            PublicSafetyRiskType.MENTAL_HEALTH_CRISIS: [
                "psychotic episode", "hearing voices", "not taking meds",
                "delusional", "psychiatric emergency"
            ]
        }

    @staticmethod
    def get_safe_response(risk_type: PublicSafetyRiskType) -> str:
        responses = {
            PublicSafetyRiskType.CRISIS:
                "🚨 If you are in immediate danger, call 911 now. "
                "I am creating an urgent case for emergency services. "
                "Help is being dispatched. Stay on the line if you can.",

            PublicSafetyRiskType.DOMESTIC_VIOLENCE:
                "You are not alone, and this is not your fault. Your safety is most important. "
                "National Domestic Violence Hotline: 1-800-799-7233. "
                "Would you like me to connect you with local resources and a safe place to go?",

            PublicSafetyRiskType.HOMELESSNESS:
                "I'm connecting you with emergency housing resources. "
                "In the meantime, here are the nearest shelters that have availability tonight. "
                "A caseworker will contact you within 30 minutes.",

            PublicSafetyRiskType.CHILD_ENDANGERMENT:
                "Thank you for reporting this. Children's safety is our highest priority. "
                "A child protective services caseworker is being assigned immediately. "
                "This report is mandatory and will be investigated."
        }
        return responses.get(risk_type,
            "Your situation is important. Connecting you with appropriate resources now.")

    @staticmethod
    def assign_responder(risk_type: PublicSafetyRiskType) -> str:
        routing = {
            PublicSafetyRiskType.CRISIS: "911_dispatch",
            PublicSafetyRiskType.DOMESTIC_VIOLENCE: "dv_advocate",
            PublicSafetyRiskType.HOMELESSNESS: "housing_caseworker",
            PublicSafetyRiskType.CHILD_ENDANGERMENT: "cps_investigator",
            PublicSafetyRiskType.ELDER_ABUSE: "aps_caseworker",
            PublicSafetyRiskType.MENTAL_HEALTH_CRISIS: "crisis_intervention_team",
            PublicSafetyRiskType.SUBSTANCE_CRISIS: "substance_counselor"
        }
        return routing.get(risk_type, "social_services_caseworker")

    @staticmethod
    def get_timeout_minutes(risk_type: PublicSafetyRiskType) -> int:
        immediate = [PublicSafetyRiskType.CRISIS, PublicSafetyRiskType.CHILD_ENDANGERMENT]
        if risk_type in immediate:
            return 5  # 5 minutes
        urgent = [PublicSafetyRiskType.DOMESTIC_VIOLENCE, PublicSafetyRiskType.MENTAL_HEALTH_CRISIS]
        if risk_type in urgent:
            return 15  # 15 minutes
        return 30  # 30 minutes for all others

    @staticmethod
    def get_mandatory_reporters() -> List[PublicSafetyRiskType]:
        """Roles that trigger mandatory reporting to authorities"""
        return [
            PublicSafetyRiskType.CHILD_ENDANGERMENT,
            PublicSafetyRiskType.ELDER_ABUSE,
            PublicSafetyRiskType.CRISIS
        ]
