"""
Backend for Mark Kimuyu's research/freelance website.
----------------------------------------------------
Serves the static site (index.html) and handles the contact form by
emailing submissions to your Gmail inbox via SMTP.

Required environment variables:
  GMAIL_ADDRESS      - the Gmail account sending notifications (e.g. markkimuyu2@gmail.com)
  GMAIL_APP_PASSWORD - a 16-character Gmail App Password (NOT your normal password)
  NOTIFY_EMAIL       - where form submissions should be sent (can be same as GMAIL_ADDRESS)
"""

import os
import re
import smtplib
import logging
from email.message import EmailMessage

from flask import Flask, request, jsonify, send_from_directory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=".", static_url_path="")

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", GMAIL_ADDRESS)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Very small in-memory rate limiter: max 5 submissions per IP per hour.
from collections import defaultdict
from time import time

_submission_log = defaultdict(list)
RATE_LIMIT = 5
RATE_WINDOW_SECONDS = 3600


def is_rate_limited(ip: str) -> bool:
    now = time()
    recent = [t for t in _submission_log[ip] if now - t < RATE_WINDOW_SECONDS]
    _submission_log[ip] = recent
    return len(recent) >= RATE_LIMIT


def record_submission(ip: str) -> None:
    _submission_log[ip].append(time())


def send_notification_email(name: str, email: str, project_type: str, details: str) -> None:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "GMAIL_ADDRESS / GMAIL_APP_PASSWORD environment variables are not set."
        )

    msg = EmailMessage()
    msg["Subject"] = f"New project inquiry from {name}"
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = NOTIFY_EMAIL
    msg["Reply-To"] = email  # so hitting "reply" in your inbox goes straight to the client

    msg.set_content(
        f"""New contact form submission from your website.

Name: {name}
Email: {email}
Project type: {project_type}

Details:
{details}

---
Reply directly to this email to respond to {name}.
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")


@app.route("/api/contact", methods=["POST"])
def contact():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if is_rate_limited(ip):
        return jsonify({"error": "Too many submissions. Please try again later."}), 429

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    project_type = (data.get("type") or "Not specified").strip()
    details = (data.get("details") or "").strip()

    # Basic validation
    if not name or not email or not details:
        return jsonify({"error": "Please fill in your name, email, and project details."}), 400

    if not EMAIL_RE.match(email):
        return jsonify({"error": "Please enter a valid email address."}), 400

    if len(details) > 5000:
        return jsonify({"error": "Message is too long. Please shorten it."}), 400

    try:
        send_notification_email(name, email, project_type, details)
    except Exception:
        logger.exception("Failed to send notification email")
        return jsonify({"error": "Could not send your message right now. Please email directly instead."}), 500

    record_submission(ip)
    logger.info("Contact form submission from %s <%s>", name, email)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
