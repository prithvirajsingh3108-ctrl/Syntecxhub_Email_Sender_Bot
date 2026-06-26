# ✉️ Syntecxhub Email Sender Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Internship](https://img.shields.io/badge/Internship-Task%203-purple?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

**Python Programming Internship — Task 3 @ Syntecxhub**

*A production-ready bulk email automation system with a Streamlit dashboard, retry logic, CSV logging, and full input validation.*

[Features](#-features) · [Project Structure](#-project-structure) · [Setup](#-setup) · [CLI Usage](#-cli-usage) · [Dashboard](#-streamlit-dashboard) · [Architecture](#-architecture--code-walkthrough) · [FAQ](#-faq)

</div>

---

## 📌 Overview

**Syntecxhub Email Sender Bot** is a complete, professional-grade email automation tool built entirely in Python. It reads a list of recipients from a CSV file, personalises each email using a template with `{name}` and `{company}` placeholders, attaches files automatically, retries failed sends, and logs every attempt to a CSV file.

The project ships in two modes:

| Mode | How to run | Best for |
|---|---|---|
| **CLI** | `python3 main.py` | Scheduled jobs, servers, scripting |
| **Streamlit Dashboard** | `streamlit run app.py` | Visual control, non-technical users |

Both modes share the same core `src/` library, so behaviour is identical regardless of how you trigger it.

---

## ✨ Features

### Core Email Features
- **Bulk sending** — iterate over every row in a CSV, send one personalised email each
- **Personalisation** — `{name}` and `{company}` placeholders are replaced per recipient
- **Per-recipient subjects** — each row in the CSV can have a unique subject line
- **Attachment support** — every file inside `attachments/` is attached to every email
- **Gmail SMTP** — uses `smtplib` with STARTTLS encryption on port 587

### Reliability
- **3-attempt retry logic** — on transient failures the bot waits and retries up to 3 times with exponential back-off (2 s, 4 s)
- **Graceful error handling** — authentication errors and refused recipients are not retried (no point wasting attempts)
- **Per-recipient isolation** — one bad address never stops the rest of the send run

### Validation & Safety
- Detects missing CSV file before starting
- Detects missing template file before starting
- Detects missing attachments folder before starting
- Validates every email address against RFC-style regex — skips invalid rows with a warning
- Skips rows with empty email fields
- Catches missing CSV columns and reports them clearly
- Verifies SMTP credentials with a live test connection before sending any emails
- All credentials stored in `.env` — never hardcoded, never committed

### Logging
- Every send attempt (success or failure) is appended to `logs/email_log.csv`
- Log fields: `timestamp`, `recipient_name`, `recipient_email`, `subject`, `status`, `error_message`
- Log file is created automatically on first run if it doesn't exist

### Developer Experience
- **Dry-run mode** — renders and prints every personalised email to the terminal without sending a single one; safe for testing and demos
- **Colour-coded terminal output** — green ticks for success, red crosses for failure, yellow warnings
- **Modular architecture** — each concern lives in its own file inside `src/`
- **Beginner-friendly code** — every module, class, and function is documented with docstrings and inline comments

### Streamlit Dashboard (app.py)
- Upload CSV directly in the browser
- Edit the email template in a live text area
- Upload attachment files from your machine
- Preview the personalised email with sample values before sending
- Send emails with a single button click
- Real-time progress bar and per-recipient status messages
- Success / failure metric cards after the run
- Full log table with colour-coded status column
- Download logs as CSV with one click
- SMTP credential tester built into the sidebar
- Clean, dark-themed modern UI

---

## 📁 Project Structure

```
Syntecxhub_Email_Sender_Bot/
│
├── main.py                  # CLI entry point — argument parsing, orchestration
├── app.py                   # Streamlit dashboard — all UI code
│
├── recipients.csv           # Sample recipient list (replace with your own data)
├── email_template.txt       # Plain-text email body with {name}/{company} placeholders
│
├── requirements.txt         # Pinned Python dependencies
├── .env.example             # Credential template — safe to commit, copy to .env
├── .gitignore               # Keeps .env and caches out of git
├── LICENSE                  # MIT License
├── README.md                # This file
│
├── attachments/             # Drop any files here — they get attached to every email
│   └── sample_report.txt   # Placeholder — replace with your real PDF/DOCX/etc.
│
├── logs/
│   └── email_log.csv       # Auto-generated send log (created on first run)
│
└── src/                     # Core library — shared by both CLI and Streamlit
    ├── __init__.py          # Marks src/ as a Python package
    ├── config.py            # Reads .env into a typed Config class
    ├── csv_reader.py        # Parses CSV → list of Recipient dataclasses
    ├── email_builder.py     # Builds MIMEMultipart message objects
    ├── sender.py            # SMTP connection + 3-attempt retry logic
    ├── logger.py            # Appends rows to the CSV log file
    └── validators.py        # File, email-format, and SMTP credential validators
```

---

## 🏗️ Architecture & Code Walkthrough

Understanding how the pieces fit together will help you customise the project or debug issues confidently.

### Data Flow (CLI)

```
main.py
  │
  ├── parse_args()           ← reads --csv, --template, --attachments, --dry-run
  │
  ├── run_validations()
  │     ├── Config.validate()          → checks .env variables exist
  │     ├── validate_csv_file()        → checks file exists + .csv extension
  │     ├── validate_template_file()   → checks file exists
  │     ├── validate_attachments_folder() → checks folder exists
  │     └── validate_smtp_credentials()   → live SMTP login test (skipped in dry-run)
  │
  ├── read_recipients(csv_path)
  │     └── returns List[Recipient] + warnings for skipped rows
  │
  ├── load_template(template_path)
  │     └── returns raw string with {name}/{company} placeholders
  │
  └── send_all()  OR  preview_emails()
        │
        ├── build_email(sender, recipient, template, attachments_folder)
        │     ├── personalise_body()   → replaces placeholders
        │     ├── MIMEText(body)       → attaches plain-text body
        │     └── MIMEBase(file)       → attaches each file in attachments/
        │
        ├── send_email(msg)
        │     └── SMTP login → sendmail → retry on transient error
        │
        └── log_result(...)
              └── appends one row to logs/email_log.csv
```

### Module Responsibilities

#### `src/config.py`
Loads the four environment variables (`EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`) from the `.env` file using `python-dotenv`. The `Config` class exposes them as typed class attributes and provides a `validate()` method that returns a list of error strings (empty list = all good). This keeps credential access centralised — only `config.py` and `sender.py` ever touch credentials.

#### `src/csv_reader.py`
Opens the CSV with `csv.DictReader`, normalises column names to lowercase, and builds a `Recipient` dataclass per valid row. Invalid rows (empty email, bad format, missing) are skipped and their issues added to a warnings list that is displayed in the terminal but does not stop the run. The function signature is `read_recipients(path) → (list[Recipient], list[str])`.

#### `src/email_builder.py`
Contains three focused functions:
- `load_template(path)` — reads `email_template.txt` into a string
- `personalise_body(template, recipient)` — applies `.replace()` for each placeholder
- `build_email(sender, recipient, template, attachments_folder)` — assembles the `MIMEMultipart` object, attaches the body as `MIMEText`, then iterates over files in the attachments folder and appends each as a `MIMEBase` part with `base64` encoding

#### `src/sender.py`
Opens a fresh `smtplib.SMTP` context for each attempt (avoids stale connection issues), calls `ehlo()`, upgrades to TLS with `starttls()`, logs in, and calls `sendmail()`. On success it returns `(True, "")`. On `SMTPAuthenticationError` or `SMTPRecipientsRefused` it returns immediately without retrying (retrying won't fix these). On any other exception it waits `attempt × 2` seconds and tries again, up to `MAX_RETRIES = 3`.

#### `src/logger.py`
Uses `csv.DictWriter` in append mode. On first write it creates the `logs/` directory and writes the header row. Every subsequent call just appends one data row. The `log_result()` function is intentionally simple with no external dependencies so it can be called from both `main.py` and `app.py`.

#### `src/validators.py`
Five independent validator functions, each returning either `None` (valid) or a descriptive error string. They are called sequentially in `main.py`'s `run_validations()`. The SMTP validator is a real network call — it opens a connection, authenticates, and closes it — so it's skipped in dry-run mode.

---

## ⚙️ Setup

### Prerequisites

- Python **3.10 or newer** (uses modern type hint syntax like `list[str]`)
- A **Gmail account** with 2-Step Verification enabled
- A **Gmail App Password** (see below)

### 1 · Clone the repository

```bash
git clone https://github.com/prithvirajsingh/Syntecxhub_Email_Sender_Bot.git
cd Syntecxhub_Email_Sender_Bot
```

### 2 · Create and activate a virtual environment

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate.bat

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Configure credentials

```bash
cp .env.example .env      # macOS/Linux
copy .env.example .env    # Windows
```

Open `.env` in any text editor and fill in your real values:

```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

> ⚠️ **Important:** The `.env` file is listed in `.gitignore`. It will never be committed to git. Never share it or add it to version control.

---

## 🔑 How to Create a Gmail App Password

Gmail blocks direct password authentication for SMTP. You need a special **App Password** — a 16-character token that acts as a one-time password scoped to a single app.

**Step-by-step:**

1. Sign in to your Google Account at [myaccount.google.com](https://myaccount.google.com)
2. Go to **Security** in the left sidebar
3. Under *"How you sign in to Google"*, click **2-Step Verification** and make sure it is **On**
4. In the Google Account search bar at the top, type **App passwords** and select the result
5. You may be asked to re-enter your password
6. Under *"Select app"* choose **Mail**; under *"Select device"* choose **Other (custom name)** and type `EmailSenderBot`
7. Click **Generate**
8. Copy the 16-character password shown (e.g. `abcd efgh ijkl mnop`)
9. Paste it as the value of `EMAIL_APP_PASSWORD` in your `.env` file — spaces are fine

> 💡 You can revoke an App Password at any time from the same page without affecting your main Gmail password.

---

## 📋 Recipients CSV Format

The CSV file must contain these **four columns** (order doesn't matter, case-insensitive):

| Column | Required | Description |
|---|---|---|
| `name` | ✅ | Recipient's full name — used in `{name}` placeholder |
| `email` | ✅ | Valid email address — rows with empty or invalid email are skipped |
| `company` | ✅ | Company or organisation name — used in `{company}` placeholder |
| `subject` | ✅ | Email subject line — can be unique per row |

**Example:**

```csv
name,email,company,subject
Alice Johnson,alice@example.com,Acme Corp,Exciting Opportunity for Acme Corp
Bob Smith,bob@example.com,Beta Solutions,Partnership Proposal for Beta Solutions
Carol White,carol@example.com,Creative Labs,Collaboration Invitation
David Brown,david@example.com,Delta Systems,Special Offer for Delta Systems
```

**Validation rules applied per row:**
- Empty `email` field → row skipped, warning printed
- Email doesn't match `^[\w\.-]+@[\w\.-]+\.\w{2,}$` → row skipped, warning printed
- Missing required column in the file → entire file rejected with a clear error

---

## 📧 Email Template Guide

The template is a plain `.txt` file. Use these placeholders anywhere in the body:

| Placeholder | Replaced with |
|---|---|
| `{name}` | The recipient's name from the CSV |
| `{company}` | The recipient's company from the CSV |

**Example template (`email_template.txt`):**

```
Dear {name},

I hope this message finds you well.

I'm reaching out to connect with {company} regarding an exciting opportunity...

We look forward to hearing from you, {name}.

Warm regards,
[Your Name]
Syntecxhub
```

> **Tip:** You can use `{name}` and `{company}` multiple times in the same template. Every occurrence is replaced.

---

## 🖥️ CLI Usage

```bash
# Send emails using default file paths
python3 main.py

# Specify all paths explicitly
python3 main.py \
  --csv recipients.csv \
  --template email_template.txt \
  --attachments attachments/

# Preview emails without sending (safe for testing)
python3 main.py --dry-run

# Dry-run with a custom CSV
python3 main.py --csv my_contacts.csv --dry-run
```

### CLI Arguments Reference

| Argument | Default | Description |
|---|---|---|
| `--csv PATH` | `recipients.csv` | Path to the recipients CSV file |
| `--template PATH` | `email_template.txt` | Path to the plain-text email body template |
| `--attachments PATH` | `attachments/` | Path to the folder containing attachment files |
| `--dry-run` | off | Preview mode — renders every email to terminal, sends nothing |

### What the CLI output looks like

```
╔══════════════════════════════════════════╗
║   Syntecxhub Email Sender Bot  v1.0.0   ║
║   Python Internship — Task 3            ║
╚══════════════════════════════════════════╝

── Running pre-flight checks ────────────────
✔  All pre-flight checks passed.

── Loading recipients ───────────────────────
✔  Loaded 5 valid recipient(s).

── Sending emails to 5 recipient(s) ─────────
ℹ  [1/5] Sending to Alice Johnson <alice@example.com>...
✔    Sent successfully → alice@example.com
ℹ  [2/5] Sending to Bob Smith <bob@example.com>...
✔    Sent successfully → bob@example.com
...

── Summary ───────────────────────────────────
✔  Emails sent successfully : 5
ℹ  Full log saved to        : logs/email_log.csv
```

---

## 🌐 Streamlit Dashboard

```bash
streamlit run app.py
```

Opens at **[http://localhost:8501](http://localhost:8501)** in your default browser.

### Tab Guide

| Tab | What you can do |
|---|---|
| **📤 Send Emails** | Upload CSV · Edit template · Upload attachments · Enable dry-run · Send with progress bar |
| **👁️ Preview** | Enter sample name/company/subject and see the rendered email live |
| **📊 Logs** | View full send history table · See success/failed counts · Download log as CSV |
| **ℹ️ Help** | Quick-start guide, CSV format, template syntax, CLI commands |

**Sidebar** contains SMTP settings (pre-filled from `.env`) and a one-click credential tester.

---

## 📄 Log File Reference

Logs are stored at `logs/email_log.csv` and appended after every send run.

| Field | Type | Description |
|---|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM:SS` | When the send attempt completed |
| `recipient_name` | string | Name from the CSV row |
| `recipient_email` | string | Email address from the CSV row |
| `subject` | string | Subject line used |
| `status` | `SUCCESS` / `FAILED` | Outcome of the send attempt |
| `error_message` | string | Empty on success; error description on failure |

**Example log:**

```csv
timestamp,recipient_name,recipient_email,subject,status,error_message
2024-06-26 10:30:00,Alice Johnson,alice@example.com,Exciting Opportunity,SUCCESS,
2024-06-26 10:30:05,Bob Smith,bob-bad,Partnership Proposal,FAILED,Invalid email format
2024-06-26 10:30:12,Carol White,carol@example.com,Collaboration Invite,SUCCESS,
```

---

## 🔧 Customisation

### Use a different SMTP provider (Outlook, Yahoo, etc.)

Update your `.env`:

```env
# Outlook / Office 365
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587

# Yahoo Mail
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=465
```

> Note: Yahoo uses SSL on port 465. You'd need to change `smtplib.SMTP` to `smtplib.SMTP_SSL` in `src/sender.py`.

### Add more placeholders

In `src/email_builder.py`, extend `personalise_body()`:

```python
def personalise_body(template: str, recipient: Recipient) -> str:
    body = template.replace("{name}", recipient.name)
    body = body.replace("{company}", recipient.company)
    body = body.replace("{role}", recipient.role)   # ← add new ones here
    return body
```

Then add the new column to your CSV and the `Recipient` dataclass in `csv_reader.py`.

### Send HTML emails

In `src/email_builder.py`, change the MIME type:

```python
# Plain text (current)
msg.attach(MIMEText(body, "plain"))

# HTML
msg.attach(MIMEText(body, "html"))
```

Your template can then contain full HTML markup.

---

## 🛡️ Security Best Practices

| Practice | How this project implements it |
|---|---|
| No hardcoded credentials | All secrets live in `.env` only |
| `.env` excluded from git | `.gitignore` covers `.env` |
| App Password instead of main password | Documented in setup; revocable any time |
| STARTTLS encryption | `server.starttls()` called before every login |
| Input validation before sending | All inputs validated in `validators.py` before any SMTP connection |
| Minimal dependency surface | Only 3 third-party packages (`pandas`, `python-dotenv`, `streamlit`) |

---

## 🐛 Troubleshooting

| Error | Likely cause | Fix |
|---|---|---|
| `No module named 'dotenv'` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `EMAIL_ADDRESS is missing` | `.env` file not created | Run `cp .env.example .env` and fill it in |
| `SMTPAuthenticationError` | Wrong app password or 2FA not enabled | Re-generate app password; ensure 2-Step Verification is on |
| `SMTPConnectError` | Firewall or wrong SMTP host/port | Check `SMTP_SERVER` and `SMTP_PORT` in `.env` |
| `CSV is missing required columns` | Column names don't match expected | Rename columns to `name`, `email`, `company`, `subject` |
| `Recipient refused` | Address doesn't exist | Fix the email address in the CSV |
| Streamlit page is blank | Streamlit not installed | Run `pip install streamlit` |

---

## 🔮 Future Improvements

- [ ] **HTML email support** — rich formatting, images, branded templates
- [ ] **Email scheduling** — send at a specific date/time using `schedule` or `APScheduler`
- [ ] **Unsubscribe handling** — honour opt-out list, append unsubscribe footer
- [ ] **Open/click tracking** — invisible pixel or link wrapping to measure engagement
- [ ] **Multi-threaded sending** — `ThreadPoolExecutor` for large lists (1 000+ recipients)
- [ ] **Rate limiting** — respect Gmail's 500 emails/day limit with a counter
- [ ] **Outlook / Office 365 support** — `SMTP_SSL` mode for port 465
- [ ] **Database backend** — store recipients and logs in SQLite or PostgreSQL
- [ ] **Auth for dashboard** — protect Streamlit UI with a login page
- [ ] **Email preview as HTML** — render template as HTML in the Preview tab

---

## 🖼️ Screenshots

> *Add screenshots here after running the project.*

| CLI — Dry Run | CLI — Live Send |
|---|---|
| *(add screenshot)* | *(add screenshot)* |

| Streamlit — Send Tab | Streamlit — Logs Tab |
|---|---|
| *(add screenshot)* | *(add screenshot)* |

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

You are free to use, copy, modify, and distribute this project for personal or commercial purposes with attribution.

---

## 👤 Author

**Prithviraj Singh**
Python Programming Intern @ Syntecxhub

- 📧 prithvirajsingh3108@gmail.com
- 🔗 [GitHub](https://github.com/prithvirajsingh)
- 💼 [LinkedIn](https://linkedin.com/in/prithvirajsingh)

---

## 🙏 Acknowledgements

- [Python smtplib documentation](https://docs.python.org/3/library/smtplib.html)
- [Streamlit documentation](https://docs.streamlit.io)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- Syntecxhub internship programme for the project brief

---

<div align="center">

Built with ❤️ using Python · smtplib · Streamlit · pandas

*If this project helped you, please give it a ⭐ on GitHub!*

</div>
