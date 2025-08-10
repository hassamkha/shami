from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class TwilioConfig:
    account_sid: str
    auth_token: str
    from_number: str

    @staticmethod
    def from_env() -> Optional["TwilioConfig"]:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
        auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
        from_number = os.getenv("TWILIO_FROM_NUMBER", "").strip()
        if not (account_sid and auth_token and from_number):
            return None
        return TwilioConfig(
            account_sid=account_sid,
            auth_token=auth_token,
            from_number=from_number,
        )


@dataclass(frozen=True)
class SendGridConfig:
    api_key: str
    from_email: str

    @staticmethod
    def from_env() -> Optional["SendGridConfig"]:
        api_key = os.getenv("SENDGRID_API_KEY", "").strip()
        from_email = os.getenv("EMAIL_FROM", "").strip()
        if not (api_key and from_email):
            return None
        return SendGridConfig(api_key=api_key, from_email=from_email)


@dataclass(frozen=True)
class AppConfig:
    twilio: Optional[TwilioConfig]
    sendgrid: Optional[SendGridConfig]

    @staticmethod
    def load() -> "AppConfig":
        return AppConfig(
            twilio=TwilioConfig.from_env(),
            sendgrid=SendGridConfig.from_env(),
        )