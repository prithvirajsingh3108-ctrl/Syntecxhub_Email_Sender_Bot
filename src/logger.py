# src/logger.py
# Appends send results to the CSV log file

import csv
import os
from datetime import datetime

# Column headers for the log file
LOG_FIELDS = [
    "timestamp",
    "recipient_name",
    "recipient_email",
    "subject",
    "status",
    "error_message",
]


def _ensure_log_file(log_path: str) -> None:
    """
    Create the log file with headers if it does not already exist.
    Also creates the parent directory if needed.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    if not os.path.isfile(log_path):
        with open(log_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
            writer.writeheader()


def log_result(
    log_path: str,
    recipient_name: str,
    recipient_email: str,
    subject: str,
    success: bool,
    error_message: str = "",
) -> None:
    """
    Append one row to the email log CSV.

    Args:
        log_path:         Full path to the log CSV file.
        recipient_name:   Name of the recipient.
        recipient_email:  Email address of the recipient.
        subject:          Email subject line.
        success:          True if the email was sent successfully.
        error_message:    Description of the error if sending failed.
    """
    _ensure_log_file(log_path)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "recipient_name": recipient_name,
        "recipient_email": recipient_email,
        "subject": subject,
        "status": "SUCCESS" if success else "FAILED",
        "error_message": error_message,
    }

    with open(log_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        writer.writerow(row)
