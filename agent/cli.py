from __future__ import annotations

import argparse
import sys
from typing import Optional

from agent.agent import NotificationAgent
from agent.config import AppConfig


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call & Email Agent CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    call_parser = subparsers.add_parser("call", help="Place a phone call and speak a message")
    call_parser.add_argument("--to", required=True, help="Destination phone number in E.164 format (e.g. +15551234567)")
    call_parser.add_argument("--message", required=True, help="Message to speak during the call")

    email_parser = subparsers.add_parser("email", help="Send an email message")
    email_parser.add_argument("--to", required=True, help="Recipient email address")
    email_parser.add_argument("--subject", required=True, help="Email subject")
    email_parser.add_argument("--text", required=True, help="Plain text body")
    email_parser.add_argument("--html", required=False, help="Optional HTML body")

    notify_parser = subparsers.add_parser("notify", help="Send both a call and an email")
    notify_parser.add_argument("--to-phone", required=True, help="Destination phone number in E.164 format")
    notify_parser.add_argument("--to-email", required=True, help="Recipient email address")
    notify_parser.add_argument("--subject", required=True, help="Email subject")
    notify_parser.add_argument("--message", required=True, help="Message to speak and to send as text body")
    notify_parser.add_argument("--html", required=False, help="Optional HTML body for the email")

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    config = AppConfig.load()
    agent = NotificationAgent(config)

    try:
        if args.command == "call":
            result = agent.call_user(to_number=args.to, message=args.message)
            print(f"Call placed. SID={result.call_sid} to={result.to_number}")
        elif args.command == "email":
            result = agent.email_user(
                to_email=args.to, subject=args.subject, text=args.text, html=args.html
            )
            print(f"Email sent. status={result.status_code} to={result.to_email}")
        elif args.command == "notify":
            result = agent.notify_both(
                to_number=args.to_phone,
                to_email=args.to_email,
                subject=args.subject,
                message=args.message,
                html=args.html,
            )
            parts = []
            if result.call:
                parts.append(f"call(SID={result.call.call_sid})")
            if result.email:
                parts.append(f"email(status={result.email.status_code})")
            print("Completed: " + ", ".join(parts) if parts else "No actions performed")
        else:
            parser.error("Unknown command")
            return 2
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())