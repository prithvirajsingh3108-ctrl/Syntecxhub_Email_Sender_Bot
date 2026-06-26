# src/email_builder.py
# Builds the MIMEMultipart email message with body and attachments

import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from src.csv_reader import Recipient


def load_template(template_path: str) -> str:
    """Read the email body template from a .txt file."""
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def personalise_body(template: str, recipient: Recipient) -> str:
    """
    Replace {name} and {company} placeholders in the template
    with the recipient's actual values.
    """
    body = template.replace("{name}", recipient.name)
    body = body.replace("{company}", recipient.company)
    return body


def get_attachments(attachments_folder: str) -> list[str]:
    """
    Return a list of full file paths for every file inside the
    attachments folder. Subdirectories are ignored.
    """
    if not os.path.isdir(attachments_folder):
        return []
    return [
        os.path.join(attachments_folder, fname)
        for fname in os.listdir(attachments_folder)
        if os.path.isfile(os.path.join(attachments_folder, fname))
    ]


def build_email(
    sender: str,
    recipient: Recipient,
    template: str,
    attachments_folder: str,
) -> MIMEMultipart:
    """
    Construct the full email message object.

    Args:
        sender:              The sender's email address.
        recipient:           Recipient dataclass with name, email, company, subject.
        template:            Raw template string (may contain placeholders).
        attachments_folder:  Path to the folder containing attachment files.

    Returns:
        A MIMEMultipart message ready to be sent via smtplib.
    """
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient.email
    msg["Subject"] = recipient.subject

    # Personalise and attach the plain-text body
    body = personalise_body(template, recipient)
    msg.attach(MIMEText(body, "plain"))

    # Attach every file found in the attachments folder
    for file_path in get_attachments(attachments_folder):
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={filename}",
            )
            msg.attach(part)
        except OSError as exc:
            # Non-fatal: log and skip the problematic file
            print(f"  [WARNING] Could not attach '{filename}': {exc}")

    return msg
