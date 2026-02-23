from enum import Enum
from typing import List, Dict


class CommerceRiskType(str, Enum):
    SCAM = "scam"
    FRAUD = "fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    PAYMENT_DISPUTE = "payment_dispute"
    THREATENING_CUSTOMER = "threatening_customer"
    ABUSIVE_SELLER = "abusive_seller"
    UNSAFE_PRODUCT = "unsafe_product"
    IDENTITY_THEFT = "identity_theft"


class CommerceSafetyDomain:
    @staticmethod
    def get_risk_patterns() -> Dict[CommerceRiskType, List[str]]:
        return {
            CommerceRiskType.SCAM: [
                "sent money but no product",
                "fake seller",
                "won't refund",
                "never received",
                "took my money",
                "obvious scam",
            ],
            CommerceRiskType.FRAUD: [
                "unauthorized charges",
                "didn't make this purchase",
                "credit card fraud",
                "someone used my account",
            ],
            CommerceRiskType.ACCOUNT_TAKEOVER: [
                "can't log in",
                "password changed",
                "locked out",
                "someone accessed my account",
                "hacked",
            ],
            CommerceRiskType.THREATENING_CUSTOMER: [
                "find you",
                "you'll regret",
                "come to your house",
                "threatening messages",
                "harassing",
            ],
            CommerceRiskType.UNSAFE_PRODUCT: [
                "product caught fire",
                "chemical burn",
                "child injured",
                "dangerous defect",
                "safety hazard",
                "recall",
            ],
            CommerceRiskType.IDENTITY_THEFT: [
                "used my identity",
                "opened account in my name",
                "stolen personal info",
                "fake account",
            ],
        }

    @staticmethod
    def get_safe_response(risk_type: CommerceRiskType) -> str:
        responses = {
            CommerceRiskType.FRAUD: "I'm flagging this transaction immediately and freezing your account for protection. "
            "Our fraud team will contact you within 1 hour. "
            "You will not be responsible for unauthorized charges.",
            CommerceRiskType.SCAM: "Thank you for reporting this. I'm documenting this case for our fraud investigation team. "
            "We'll work to recover your funds and prevent this seller from targeting others. "
            "Case number: [AUTO-GENERATED]",
            CommerceRiskType.THREATENING_CUSTOMER: "This behavior violates our terms of service and potentially criminal law. "
            "I'm escalating this to our safety team and law enforcement if appropriate. "
            "Your safety is our priority. Would you like us to involve authorities?",
            CommerceRiskType.UNSAFE_PRODUCT: "This is a serious safety concern. I'm immediately flagging this product and "
            "notifying our safety compliance team. "
            "Please seek medical attention if needed. We'll issue a full refund immediately.",
        }
        return responses.get(
            risk_type,
            "Your concern is being escalated to the appropriate team for immediate action.",
        )

    @staticmethod
    def assign_responder(risk_type: CommerceRiskType) -> str:
        routing = {
            CommerceRiskType.FRAUD: "fraud_investigator",
            CommerceRiskType.SCAM: "fraud_investigator",
            CommerceRiskType.ACCOUNT_TAKEOVER: "security_team",
            CommerceRiskType.THREATENING_CUSTOMER: "trust_safety_team",
            CommerceRiskType.UNSAFE_PRODUCT: "product_safety_team",
            CommerceRiskType.IDENTITY_THEFT: "fraud_investigator",
        }
        return routing.get(risk_type, "customer_support_supervisor")

    @staticmethod
    def get_timeout_minutes(risk_type: CommerceRiskType) -> int:
        immediate = [CommerceRiskType.THREATENING_CUSTOMER, CommerceRiskType.UNSAFE_PRODUCT]
        if risk_type in immediate:
            return 15  # 15 minutes for urgent
        elif risk_type in [CommerceRiskType.FRAUD, CommerceRiskType.ACCOUNT_TAKEOVER]:
            return 60  # 1 hour
        else:
            return 240  # 4 hours
