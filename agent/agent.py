from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from agent.config import AppConfig
from agent.services.call_service import CallService, CallResult
from agent.services.email_service import EmailService, EmailResult


@dataclass
class NotificationResult:
    call: Optional[CallResult]
    email: Optional[EmailResult]


class NotificationAgent:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._call_service: Optional[CallService] = (
            CallService(config.twilio) if config.twilio else None
        )
        self._email_service: Optional[EmailService] = (
            EmailService(config.sendgrid) if config.sendgrid else None
        )

    def call_user(self, to_number: str, message: str) -> CallResult:
        if not self._call_service:
            raise RuntimeError("Twilio is not configured. Set TWILIO_* env vars.")
        return self._call_service.make_call(to_number=to_number, message=message)

    def email_user(
        self, to_email: str, subject: str, text: str, html: Optional[str] = None
    ) -> EmailResult:
        if not self._email_service:
            raise RuntimeError("SendGrid is not configured. Set SENDGRID_* env vars.")
        return self._email_service.send_email(
            to_email=to_email, subject=subject, plain_text=text, html=html
        )

    def notify_both(
        self,
        to_number: str,
        to_email: str,
        subject: str,
        message: str,
        html: Optional[str] = None,
    ) -> NotificationResult:
        call_result: Optional[CallResult] = None
        email_result: Optional[EmailResult] = None

        if self._call_service:
            call_result = self._call_service.make_call(
                to_number=to_number, message=message
            )
        if self._email_service:
            email_result = self._email_service.send_email(
                to_email=to_email, subject=subject, plain_text=message, html=html
            )
        return NotificationResult(call=call_result, email=email_result)