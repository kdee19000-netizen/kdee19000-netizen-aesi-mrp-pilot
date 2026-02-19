"""
Notification Service

Sends email, SMS, and Telegram notifications for critical risk events.
Implementations are stubs – configure credentials via .env to activate.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    async def send_email(to: str, subject: str, body: str) -> bool:
        """Send an email via SendGrid (if configured)."""
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key or api_key == "your-sendgrid-key":
            logger.warning("SendGrid not configured – email not sent to %s", to)
            return False
        try:
            import sendgrid  # type: ignore
            from sendgrid.helpers.mail import Mail  # type: ignore

            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            message = Mail(
                from_email=os.getenv("EMAIL_FROM", "noreply@aesi-mrp.com"),
                to_emails=to,
                subject=subject,
                plain_text_content=body,
            )
            sg.send(message)
            logger.info("Email sent to %s", to)
            return True
        except Exception as exc:
            logger.error("Failed to send email: %s", exc)
            return False

    @staticmethod
    async def send_sms(to: str, body: str) -> bool:
        """Send an SMS via Twilio (if configured)."""
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE")
        if not all([sid, token, from_number]) or sid == "your-sid":
            logger.warning("Twilio not configured – SMS not sent to %s", to)
            return False
        try:
            from twilio.rest import Client  # type: ignore

            client = Client(sid, token)
            client.messages.create(body=body, from_=from_number, to=to)
            logger.info("SMS sent to %s", to)
            return True
        except Exception as exc:
            logger.error("Failed to send SMS: %s", exc)
            return False
