"""Gmail API OAuth, send, and inbox scan helpers."""

from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from app.config.settings import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def token_exists() -> bool:
    return settings.gmail_token_path.exists()


def gmail_connected() -> bool:
    return settings.gmail_oauth_ready and token_exists()


def _credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    token_path = settings.gmail_token_path
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return creds


def build_auth_url() -> str:
    from google_auth_oauthlib.flow import Flow

    if not settings.gmail_oauth_ready:
        raise RuntimeError("Set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in .env")
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.gmail_redirect_uri],
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.gmail_redirect_uri,
    )
    url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return url


def exchange_code(code: str) -> None:
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.gmail_client_id,
                "client_secret": settings.gmail_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.gmail_redirect_uri],
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.gmail_redirect_uri,
    )
    flow.fetch_token(code=code)
    settings.gmail_token_path.parent.mkdir(parents=True, exist_ok=True)
    settings.gmail_token_path.write_text(flow.credentials.to_json(), encoding="utf-8")


def _service():
    from googleapiclient.discovery import build

    creds = _credentials()
    if not creds or not creds.valid:
        raise RuntimeError("Gmail is not connected. Open Settings and connect Gmail.")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def send_email(
    to_email: str,
    subject: str,
    body: str,
    attachment_path: str | None = None,
) -> str:
    """Send one email through the Gmail API. Returns Gmail message id."""
    message = EmailMessage()
    sender = settings.gmail_sender_email or "me"
    message["To"] = to_email
    message["From"] = sender
    message["Subject"] = subject
    if settings.gmail_cc_email:
        message["Cc"] = settings.gmail_cc_email
    if settings.gmail_bcc_email:
        message["Bcc"] = settings.gmail_bcc_email
    message.set_content(body)

    if attachment_path:
        path = Path(attachment_path)
        if path.exists():
            data = path.read_bytes()
            maintype, subtype = ("application", "octet-stream")
            if path.suffix.lower() == ".pdf":
                maintype, subtype = "application", "pdf"
            elif path.suffix.lower() == ".docx":
                maintype, subtype = (
                    "application",
                    "vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            message.add_attachment(
                data,
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )

    encoded = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = _service().users().messages().send(userId="me", body={"raw": encoded}).execute()
    return str(sent.get("id") or "")


def list_inbox_snippets(max_results: int = 30) -> list[dict[str, Any]]:
    """Return recent inbox messages for reply detection."""
    service = _service()
    listing = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=max_results)
        .execute()
    )
    results: list[dict[str, Any]] = []
    for item in listing.get("messages") or []:
        detail = (
            service.users()
            .messages()
            .get(userId="me", id=item["id"], format="metadata", metadataHeaders=["From", "Subject"])
            .execute()
        )
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        results.append(
            {
                "id": item["id"],
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "snippet": detail.get("snippet", ""),
            }
        )
    return results
