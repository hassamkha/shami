from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from agent.config import SendGridConfig


@dataclass
class EmailResult:
    status_code: int
    to_email: str


class EmailService:
    def __init__(self, config: SendGridConfig) -> None:
        self._config = config
        self._client: Optional[SendGridAPIClient] = None

    def _get_client(self) -> SendGridAPIClient:
        if self._client is None:
            self._client = SendGridAPIClient(self._config.api_key)
        return self._client

    def send_email(
        self,
        to_email: str,
        subject: str,
        plain_text: str,
        html: Optional[str] = None,
    ) -> EmailResult:
        client = self._get_client()
        message = Mail(
            from_email=self._config.from_email,
            to_emails=to_email,
            subject=subject,
            plain_text_content=plain_text,
            html_content=html,
        )
        response = client.send(message)
        return EmailResult(status_code=response.status_code, to_email=to_email)