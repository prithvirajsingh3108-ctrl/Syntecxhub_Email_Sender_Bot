# app.py
# Syntecxhub Email Sender Bot — Streamlit Dashboard
# Internship Task 3 | Python Programming

import os
import io
import csv
import time
import smtplib
import tempfile
import pandas as pd
import streamlit as st
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load credentials from .env if present
load_dotenv()

LOG_PATH = os.path.join("logs", "email_log.csv")
LOG_FIELDS = ["timestamp", "recipient_name", "recipient_email",
              "subject", "status", "error_message"]

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Syntecxhub Email Sender Bot",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main header gradient */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .subtitle {
        color: #888;
        font-size: 1rem;
        margin-top: 0;
    }
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #1e1e2e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 12px;
    }
    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #a78bfa;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #333;
        padding-bottom: 4px;
    }
    /* Success / failure badges */
    .badge-success {
        background: #16a34a22;
        color: #4ade80;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-failed {
        background: #dc262622;
        color: #f87171;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    import re
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email.strip()))


def personalise(template: str, name: str, company: str) -> str:
    return template.replace("{name}", name).replace("{company}", company)


def append_log(name, email, subject, success, error=""):
    os.makedirs("logs", exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient_name": name,
            "recipient_email": email,
            "subject": subject,
            "status": "SUCCESS" if success else "FAILED",
            "error_message": error,
        })


def send_single(smtp_server, smtp_port, sender_email, app_password,
                to_email, subject, body, attachment_files):
    """Send one email; returns (bool success, str error)."""
    for attempt in range(1, 4):
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            for uploaded in attachment_files:
                part = MIMEBase("application", "octet-stream")
                uploaded.seek(0)
                part.set_payload(uploaded.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={uploaded.name}",
                )
                msg.attach(part)

            with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, to_email, msg.as_string())
            return True, ""
        except smtplib.SMTPAuthenticationError as e:
            return False, f"Auth error: {e}"
        except smtplib.SMTPRecipientsRefused as e:
            return False, f"Recipient refused: {e}"
        except Exception as e:
            if attempt == 3:
                return False, f"Failed after 3 attempts: {e}"
            time.sleep(attempt * 2)
    return False, "Unknown error"


def load_log() -> pd.DataFrame:
    if os.path.isfile(LOG_PATH):
        return pd.read_csv(LOG_PATH)
    return pd.DataFrame(columns=LOG_FIELDS)


# ── Sidebar — Credentials ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ SMTP Settings")
    sender_email   = st.text_input("📧 Your Gmail Address",
                                   value=os.getenv("EMAIL_ADDRESS", ""),
                                   placeholder="you@gmail.com")
    app_password   = st.text_input("🔑 App Password",
                                   type="password",
                                   value=os.getenv("EMAIL_APP_PASSWORD", ""),
                                   placeholder="xxxx xxxx xxxx xxxx")
    smtp_server    = st.text_input("🌐 SMTP Server",
                                   value=os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port      = st.number_input("🔌 SMTP Port",
                                     value=int(os.getenv("SMTP_PORT", "587")),
                                     min_value=1, max_value=65535)

    st.markdown("---")
    st.markdown("### 🧪 Test Connection")
    if st.button("Verify SMTP Credentials"):
        if not sender_email or not app_password:
            st.error("Please fill in email and password first.")
        else:
            with st.spinner("Connecting..."):
                try:
                    with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as s:
                        s.ehlo(); s.starttls()
                        s.login(sender_email, app_password)
                    st.success("✅ Credentials verified!")
                except smtplib.SMTPAuthenticationError:
                    st.error("❌ Authentication failed. Check your app password.")
                except Exception as e:
                    st.error(f"❌ Connection error: {e}")

    st.markdown("---")
    st.caption("Syntecxhub Email Sender Bot v1.0.0")
    st.caption("Python Internship — Task 3")


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">✉️ Syntecxhub Email Sender Bot</p>',
            unsafe_allow_html=True)
st.markdown('<p class="subtitle">Automated · Personalised · Professional</p>',
            unsafe_allow_html=True)
st.markdown("---")


# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📤 Send Emails", "👁️ Preview", "📊 Logs", "ℹ️ Help"]
)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Send Emails
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    # ── Left: Upload CSV ──────────────────────────────────────────────────────
    with col_left:
        st.markdown('<p class="section-header">1 · Recipients CSV</p>',
                    unsafe_allow_html=True)
        csv_file = st.file_uploader(
            "Upload recipients.csv",
            type=["csv"],
            help="Required columns: name, email, company, subject",
        )

        df_recipients = None
        if csv_file:
            try:
                df_recipients = pd.read_csv(csv_file)
                df_recipients.columns = df_recipients.columns.str.strip().str.lower()
                required = {"name", "email", "company", "subject"}
                missing = required - set(df_recipients.columns)
                if missing:
                    st.error(f"CSV is missing columns: {', '.join(sorted(missing))}")
                    df_recipients = None
                else:
                    st.success(f"✅ Loaded **{len(df_recipients)}** rows")
                    st.dataframe(df_recipients, use_container_width=True, height=220)
            except Exception as e:
                st.error(f"Could not read CSV: {e}")

        st.markdown('<p class="section-header">2 · Attachments (optional)</p>',
                    unsafe_allow_html=True)
        attachment_files = st.file_uploader(
            "Upload one or more attachment files",
            accept_multiple_files=True,
            help="These files will be attached to every email.",
        )
        if attachment_files:
            for a in attachment_files:
                st.caption(f"📎 {a.name}")

    # ── Right: Template editor ────────────────────────────────────────────────
    with col_right:
        st.markdown('<p class="section-header">3 · Email Template</p>',
                    unsafe_allow_html=True)

        # Load default template if file exists
        default_template = ""
        if os.path.isfile("email_template.txt"):
            with open("email_template.txt", "r", encoding="utf-8") as f:
                default_template = f.read()

        template_text = st.text_area(
            "Edit your email body (use {name} and {company} as placeholders)",
            value=default_template,
            height=280,
            placeholder="Dear {name},\n\nWe are reaching out to {company}...",
        )

        dry_run_mode = st.checkbox("🧪 Dry-run (preview only, no emails sent)",
                                   value=False)

        send_btn = st.button("🚀 Send Emails", type="primary",
                             use_container_width=True, disabled=(df_recipients is None))

    # ── Sending logic ─────────────────────────────────────────────────────────
    if send_btn and df_recipients is not None:
        if not sender_email or not app_password:
            st.error("Please enter your Gmail address and App Password in the sidebar.")
        elif not template_text.strip():
            st.error("Email template is empty. Please write a message body.")
        else:
            success_count = 0
            fail_count    = 0
            results       = []

            progress_bar = st.progress(0, text="Preparing...")
            status_box   = st.empty()
            total        = len(df_recipients)

            for idx, row in df_recipients.iterrows():
                name    = str(row.get("name", "")).strip()
                email   = str(row.get("email", "")).strip()
                company = str(row.get("company", "")).strip()
                subject = str(row.get("subject", "")).strip()

                pct = int((idx) / total * 100)
                progress_bar.progress(pct, text=f"Processing {idx+1}/{total}...")

                # Basic validation
                if not email or not is_valid_email(email):
                    fail_count += 1
                    err = "Invalid or empty email"
                    results.append({"Name": name, "Email": email,
                                    "Status": "❌ FAILED", "Note": err})
                    append_log(name, email, subject, False, err)
                    continue

                body = personalise(template_text, name, company)

                if dry_run_mode:
                    status_box.info(f"[DRY-RUN] Would send to {name} <{email}>")
                    results.append({"Name": name, "Email": email,
                                    "Status": "🧪 DRY-RUN", "Note": "Not sent"})
                    success_count += 1
                    time.sleep(0.1)
                    continue

                sent, error = send_single(
                    smtp_server, smtp_port, sender_email, app_password,
                    email, subject, body, list(attachment_files),
                )
                append_log(name, email, subject, sent, error)

                if sent:
                    success_count += 1
                    results.append({"Name": name, "Email": email,
                                    "Status": "✅ SENT", "Note": ""})
                    status_box.success(f"Sent → {name} <{email}>")
                else:
                    fail_count += 1
                    results.append({"Name": name, "Email": email,
                                    "Status": "❌ FAILED", "Note": error})
                    status_box.error(f"Failed → {email}: {error}")

                time.sleep(0.3)  # gentle rate limiting

            progress_bar.progress(100, text="Done!")
            status_box.empty()

            # Summary metrics
            st.markdown("---")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Recipients", total)
            m2.metric("✅ Sent", success_count,
                      delta=f"{success_count/total*100:.0f}%")
            m3.metric("❌ Failed", fail_count,
                      delta=f"-{fail_count}" if fail_count else "0",
                      delta_color="inverse")

            st.dataframe(pd.DataFrame(results), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Preview
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 👁️ Personalised Email Preview")
    st.caption("Fill in sample values below to preview how the template looks after substitution.")

    c1, c2 = st.columns(2)
    prev_name    = c1.text_input("Sample Name",    value="Alice Johnson")
    prev_company = c2.text_input("Sample Company", value="Acme Corp")
    prev_subject = st.text_input("Sample Subject", value="Exciting Opportunity for Acme Corp")

    preview_template = ""
    if os.path.isfile("email_template.txt"):
        with open("email_template.txt", "r", encoding="utf-8") as f:
            preview_template = f.read()

    preview_body_input = st.text_area(
        "Template (edit here to see live preview below)",
        value=preview_template,
        height=200,
    )

    st.markdown("---")
    st.markdown("#### 📨 Rendered Email")

    rendered = personalise(preview_body_input, prev_name, prev_company)
    st.markdown(f"**To:** `sample@example.com`")
    st.markdown(f"**Subject:** {prev_subject}")
    st.markdown(f"**Body:**")
    st.text(rendered)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Logs
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 📊 Email Send Logs")

    df_log = load_log()

    if df_log.empty:
        st.info("No logs yet. Send some emails to see results here.")
    else:
        # Summary stats
        total_log   = len(df_log)
        sent_log    = (df_log["status"] == "SUCCESS").sum()
        failed_log  = (df_log["status"] == "FAILED").sum()

        l1, l2, l3 = st.columns(3)
        l1.metric("Total Logged",    total_log)
        l2.metric("✅ Successful",   sent_log)
        l3.metric("❌ Failed",       failed_log)

        # Colour-code status column
        def colour_status(val):
            colour = "#4ade80" if val == "SUCCESS" else "#f87171"
            return f"color: {colour}; font-weight: bold"

        st.dataframe(
            df_log.style.applymap(colour_status, subset=["status"]),
            use_container_width=True,
            height=400,
        )

        # Download button
        csv_bytes = df_log.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Logs as CSV",
            data=csv_bytes,
            file_name=f"email_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    if st.button("🔄 Refresh Logs"):
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Help
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### ℹ️ How to Use This Tool")

    st.markdown("""
**1. Gmail App Password**
- Go to [Google Account Security](https://myaccount.google.com/security)
- Enable **2-Step Verification**
- Search for **App Passwords** → generate one for "Mail"
- Paste it in the sidebar (spaces are OK)

**2. recipients.csv format**
```
name,email,company,subject
Alice Johnson,alice@example.com,Acme Corp,Partnership Opportunity
Bob Smith,bob@example.com,Beta LLC,Invitation to Connect
```

**3. email_template.txt placeholders**
```
Dear {name},

We would like to connect with {company} regarding...
```

**4. Running the CLI instead**
```bash
python main.py --csv recipients.csv --template email_template.txt --attachments attachments/
# Dry run (no emails sent):
python main.py --dry-run
```
    """)

    st.markdown("---")
    st.caption("Built with ❤️ for Syntecxhub Python Internship — Task 3")
