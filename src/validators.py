# src/validators.py
# Input validation helpers for files, email addresses, and SMTP credentials

import os
import re
import smtplib
from src.config import Config


def validate_email_format(email: str) -> bool:
    """Return True if the email string matches a basic valid format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_csv_file(path: str) -> str | None:
    """
    Check that the CSV file exists and is readable.
    Returns an error string, or None if valid.
    """
    if not os.path.isfile(path):
        return f"CSV file not found: '{path}'"
    if not path.lower().endswith(".csv"):
        return f"File '{path}' does not appear to be a CSV file."
    return None


def validate_template_file(path: str) -> str | None:
    """
    Check that the email template file exists.
    Returns an error string, or None if valid.
    """
    if not os.path.isfile(path):
        return f"Email template file not found: '{path}'"
    return None


def validate_attachments_folder(path: str) -> str | None:
    """
    Check that the attachments folder exists.
    Returns an error string, or None if valid.
    """
    if not os.path.isdir(path):
        return f"Attachments folder not found: '{path}'"
    return None


def validate_smtp_credentials() -> str | None:
    """
    Attempt a live SMTP login to verify credentials.
    Returns an error string on failure, or None if credentials are valid.
    """
    try:
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(Config.EMAIL_ADDRESS, Config.EMAIL_APP_PASSWORD)
        return None
    except smtplib.SMTPAuthenticationError:
        return (
            "SMTP authentication failed. "
            "Check EMAIL_ADDRESS and EMAIL_APP_PASSWORD in your .env file."
        )
    except smtplib.SMTPConnectError:
        return (
            f"Could not connect to SMTP server '{Config.SMTP_SERVER}:{Config.SMTP_PORT}'. "
            "Check SMTP_SERVER and SMTP_PORT."
        )
    except Exception as exc:
        return f"SMTP validation error: {exc}"
