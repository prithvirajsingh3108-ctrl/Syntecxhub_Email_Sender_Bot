#!/usr/bin/env python3
# main.py
# Syntecxhub Email Sender Bot — CLI Entry Point
# Internship Task 3 | Python Programming

import argparse
import sys
import os

# ── Colour helpers (works on any terminal that supports ANSI) ──────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def info(msg):  print(f"{CYAN}{msg}{RESET}")
def ok(msg):    print(f"{GREEN}✔  {msg}{RESET}")
def warn(msg):  print(f"{YELLOW}⚠  {msg}{RESET}")
def fail(msg):  print(f"{RED}✘  {msg}{RESET}")
def header(msg):print(f"\n{BOLD}{CYAN}{'─'*60}\n  {msg}\n{'─'*60}{RESET}")

# ── Local imports (after PYTHONPATH includes project root) ─────────────────────
from src.config import Config
from src.validators import (
    validate_csv_file,
    validate_template_file,
    validate_attachments_folder,
    validate_smtp_credentials,
)
from src.csv_reader import read_recipients
from src.email_builder import load_template, build_email, personalise_body
from src.sender import send_email
from src.logger import log_result

LOG_PATH = os.path.join("logs", "email_log.csv")


# ── Argument parser ────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Syntecxhub Email Sender Bot",
        description="Automated bulk email sender with personalisation and attachments.",
    )
    parser.add_argument(
        "--csv",
        default="recipients.csv",
        metavar="PATH",
        help="Path to the recipients CSV file (default: recipients.csv)",
    )
    parser.add_argument(
        "--template",
        default="email_template.txt",
        metavar="PATH",
        help="Path to the email body template (default: email_template.txt)",
    )
    parser.add_argument(
        "--attachments",
        default="attachments",
        metavar="PATH",
        help="Path to the attachments folder (default: attachments/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview emails without actually sending them.",
    )
    return parser.parse_args()


# ── Pre-flight validation ──────────────────────────────────────────────────────
def run_validations(args: argparse.Namespace, dry_run: bool) -> bool:
    """
    Run all validation checks. Returns True if it's safe to proceed.
    """
    header("Running pre-flight checks")
    errors: list[str] = []

    # 1. Env / config
    config_errors = Config.validate()
    errors.extend(config_errors)

    # 2. CSV file
    csv_err = validate_csv_file(args.csv)
    if csv_err:
        errors.append(csv_err)

    # 3. Template file
    tmpl_err = validate_template_file(args.template)
    if tmpl_err:
        errors.append(tmpl_err)

    # 4. Attachments folder
    att_err = validate_attachments_folder(args.attachments)
    if att_err:
        errors.append(att_err)

    # 5. SMTP credentials (skip in dry-run to avoid unnecessary network calls)
    if not dry_run and not config_errors:
        info("Verifying SMTP credentials (this may take a moment)...")
        smtp_err = validate_smtp_credentials()
        if smtp_err:
            errors.append(smtp_err)

    if errors:
        for e in errors:
            fail(e)
        return False

    ok("All pre-flight checks passed.")
    return True


# ── Dry-run preview ────────────────────────────────────────────────────────────
def preview_emails(recipients, template: str, attachments_folder: str) -> None:
    """Print a preview of each personalised email without sending."""
    header(f"DRY-RUN — Previewing {len(recipients)} email(s)")
    for i, r in enumerate(recipients, 1):
        body = personalise_body(template, r)
        print(f"\n{BOLD}{'═'*60}{RESET}")
        print(f"{BOLD}  Email #{i}{RESET}")
        print(f"  To      : {r.email}")
        print(f"  Name    : {r.name}")
        print(f"  Company : {r.company}")
        print(f"  Subject : {r.subject}")
        print(f"\n{BOLD}  Body:{RESET}")
        for line in body.splitlines():
            print(f"  {line}")

        # List attachments
        att_files = [
            f for f in os.listdir(attachments_folder)
            if os.path.isfile(os.path.join(attachments_folder, f))
        ] if os.path.isdir(attachments_folder) else []
        if att_files:
            print(f"\n  {BOLD}Attachments:{RESET} {', '.join(att_files)}")
        print(f"{BOLD}{'═'*60}{RESET}")


# ── Main sending loop ──────────────────────────────────────────────────────────
def send_all(recipients, template: str, attachments_folder: str) -> None:
    """Build and send each email, logging every result."""
    header(f"Sending emails to {len(recipients)} recipient(s)")
    success_count = 0
    fail_count = 0

    for i, recipient in enumerate(recipients, 1):
        info(f"[{i}/{len(recipients)}] Sending to {recipient.name} <{recipient.email}>...")

        # Build the email message
        msg = build_email(
            sender=Config.EMAIL_ADDRESS,
            recipient=recipient,
            template=template,
            attachments_folder=attachments_folder,
        )

        # Attempt to send (with built-in retry logic)
        sent, error = send_email(msg)

        # Log outcome
        log_result(
            log_path=LOG_PATH,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            subject=recipient.subject,
            success=sent,
            error_message=error,
        )

        if sent:
            ok(f"  Sent successfully → {recipient.email}")
            success_count += 1
        else:
            fail(f"  Failed → {recipient.email} | {error}")
            fail_count += 1

    # Summary
    header("Summary")
    ok(f"Emails sent successfully : {success_count}")
    if fail_count:
        fail(f"Emails failed            : {fail_count}")
    info(f"Full log saved to        : {LOG_PATH}")


# ── Entry point ────────────────────────────────────────────────────────────────
def main() -> None:
    args = parse_args()
    dry_run: bool = args.dry_run

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════╗")
    print(f"║   Syntecxhub Email Sender Bot  v1.0.0   ║")
    print(f"║   Python Internship — Task 3            ║")
    print(f"╚══════════════════════════════════════════╝{RESET}")

    if dry_run:
        warn("DRY-RUN mode enabled — no emails will be sent.")

    # Validate inputs
    if not run_validations(args, dry_run):
        sys.exit(1)

    # Load recipients
    header("Loading recipients")
    recipients, warnings = read_recipients(args.csv)
    for w in warnings:
        warn(w)
    if not recipients:
        fail("No valid recipients found. Exiting.")
        sys.exit(1)
    ok(f"Loaded {len(recipients)} valid recipient(s).")

    # Load email template
    header("Loading email template")
    template = load_template(args.template)
    ok(f"Template loaded from '{args.template}'.")

    # Run or preview
    if dry_run:
        preview_emails(recipients, template, args.attachments)
    else:
        send_all(recipients, template, args.attachments)


if __name__ == "__main__":
    main()
