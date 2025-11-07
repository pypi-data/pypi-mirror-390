from typing import Optional
from pytest import raises
from datetime import datetime
from .. import sent_emails


def _get_valid_email_log() -> dict:
    return {
        "external_id": "email123",
        "template_id": "default",
        "application_id": None,
        "user_id": None,
        "document_id": None,
        "status": "pending",
        "error_message": None,
        "attempt_count": 0,
    }

def test_sent_emails_valid() -> None:
    data = _get_valid_email_log()
    assert sent_emails.SentEmails.validate(data).external_id == "email123"

def test_attempt_count_default() -> None:
    data = _get_valid_email_log()
    data["attempt_count"] = 2
    assert sent_emails.SentEmails.validate(data).attempt_count == 2

def test_status_default() -> None:
    data = _get_valid_email_log()
    data["status"] = "sent"
    assert sent_emails.SentEmails.validate(data).status == "sent"

def test_error_message_nullable() -> None:
    data = _get_valid_email_log()
    data["error_message"] = "SMTP connection failed"
    assert sent_emails.SentEmails.validate(data).error_message == "SMTP connection failed"
