# src/sender.py
# Handles SMTP connection and sending emails with retry logic

import time
import smtplib
from email.mime.multipart import MIMEMultipart
from src.config import Config

# Number of send attempts before giving up on a single recipient
MAX_RETRIES = 3
# Seconds to wait between retries (increases with each attempt)
RETRY_DELAY = 2


def send_email(msg: MIMEMultipart) -> tuple[bool, str]:
    """
    Send a single email message via Gmail SMTP with retry logic.

    Args:
        msg: The fully-built MIMEMultipart message.

    Returns:
        A tuple of (success: bool, error_message: str).
        error_message is empty string on success.
    """
    last_error = ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Open a fresh SMTP connection for every attempt
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls()           # Upgrade to encrypted connection
                server.login(Config.EMAIL_ADDRESS, Config.EMAIL_APP_PASSWORD)
                server.sendmail(
                    Config.EMAIL_ADDRESS,
                    msg["To"],
                    msg.as_string(),
                )
            return True, ""  # Success — no need to retry

        except smtplib.SMTPAuthenticationError as exc:
            # Wrong credentials — no point retrying
            return False, f"Authentication error: {exc}"

        except smtplib.SMTPRecipientsRefused as exc:
            # Recipient address rejected — no point retrying
            return False, f"Recipient refused: {exc}"

        except Exception as exc:
            last_error = str(exc)
            if attempt < MAX_RETRIES:
                wait = RETRY_DELAY * attempt
                print(
                    f"    [Attempt {attempt}/{MAX_RETRIES}] Failed: {exc}. "
                    f"Retrying in {wait}s..."
                )
                time.sleep(wait)

    return False, f"Failed after {MAX_RETRIES} attempts. Last error: {last_error}"
