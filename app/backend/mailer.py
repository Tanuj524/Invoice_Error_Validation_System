import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from .config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str) -> None:
    """Sends an email via Gmail SMTP. Raises on failure — callers decide
    whether that should surface to the user or just be logged."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    subject = "Reset your password"

    text_body = (
        "You requested a password reset.\n\n"
        f"Reset your password using this link: {reset_link}\n\n"
        "This link expires in 30 minutes. If you didn't request this, "
        "you can safely ignore this email."
    )

    html_body = f"""
    <div style="font-family: sans-serif; max-width: 480px; margin: auto;">
        <h2>Reset your password</h2>
        <p>You requested a password reset for your account.</p>
        <p>
            <a href="{reset_link}"
               style="display:inline-block;padding:10px 20px;background:#2563eb;
                      color:#fff;text-decoration:none;border-radius:6px;">
                Reset Password
            </a>
        </p>
        <p style="color:#666;font-size:13px;">
            This link expires in 30 minutes. If you didn't request this,
            you can safely ignore this email.
        </p>
    </div>
    """

    try:
        send_email(to_email, subject, html_body, text_body)
    except Exception:
        # Don't let email delivery failures crash the request or leak
        # SMTP errors to the client — log it, the endpoint still returns
        # its generic success message either way.
        logger.exception("Failed to send password reset email to %s", to_email)