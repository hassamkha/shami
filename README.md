# Call & Email Agent

A minimal Python agent that can place voice calls (Twilio) and send emails (SendGrid). It provides a simple CLI to trigger actions.

## Features
- Place a phone call and speak a message using text-to-speech
- Send an email (plain text and optional HTML)
- Notify via both call and email in one command
- Environment-based configuration

## Prerequisites
- Python 3.10+
- Twilio account with a verified caller ID or enabled phone number
- SendGrid API key (or configure an alternative mail service later)

## Setup
1. Create and activate a virtual environment
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment
   ```bash
   cp .env.example .env
   # Fill in values in .env
   ```

## Environment Variables
- TWILIO_ACCOUNT_SID
- TWILIO_AUTH_TOKEN
- TWILIO_FROM_NUMBER  # E.164 format, e.g. +15551234567
- SENDGRID_API_KEY
- EMAIL_FROM          # e.g. notifications@example.com

## Usage
- Show help
  ```bash
  python -m agent.cli --help
  ```

- Make a call
  ```bash
  python -m agent.cli call --to "+15551234567" --message "Your order has shipped"
  ```

- Send an email
  ```bash
  python -m agent.cli email --to "user@example.com" --subject "Hello" --text "This is a test"
  ```

- Notify via both
  ```bash
  python -m agent.cli notify --to-phone "+15551234567" --to-email "user@example.com" \
    --subject "Order Update" --message "Your order is ready for pickup"
  ```

## Notes
- Twilio: The call uses TwiML with the `Say` verb and the `alice` voice by default.
- SendGrid: Emails are sent with plain text and optional HTML content.
- Extend easily by adding more channels in `agent/services/`.