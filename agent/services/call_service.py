from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from xml.sax.saxutils import escape as xml_escape

from twilio.rest import Client

from agent.config import TwilioConfig


@dataclass
class CallResult:
    call_sid: str
    to_number: str


class CallService:
    def __init__(self, config: TwilioConfig) -> None:
        self._config = config
        self._client: Optional[Client] = None

    def _get_client(self) -> Client:
        if self._client is None:
            self._client = Client(self._config.account_sid, self._config.auth_token)
        return self._client

    def make_call(
        self,
        to_number: str,
        message: str,
        voice: str = "alice",
        language: str = "en-US",
    ) -> CallResult:
        client = self._get_client()
        safe_message = xml_escape(message)
        twiml = f"<Response><Say voice=\"{voice}\" language=\"{language}\">{safe_message}</Say></Response>"
        call = client.calls.create(
            to=to_number,
            from_=self._config.from_number,
            twiml=twiml,
        )
        return CallResult(call_sid=call.sid, to_number=to_number)