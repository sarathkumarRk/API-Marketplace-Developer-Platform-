import smtplib
from email.mime.text import MIMEText

from app.config import settings


def send_email(to_email: str, subject: str, body: str):

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = settings.SMTP_EMAIL
    message["To"] = to_email

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD
        )

        server.sendmail(
            settings.SMTP_EMAIL,
            to_email,
            message.as_string()
        )


# 1. Subscription Activated

def send_subscription_activated_email(to_email: str):

    send_email(
        to_email,
        "Subscription Activated",
        "Your API subscription has been activated successfully."
    )


# 2. Payment Failed

def send_payment_failed_email(to_email: str):

    send_email(
        to_email,
        "Payment Failed",
        "Your API subscription payment has failed."
    )


# 3. API Approved

def send_api_approved_email(to_email: str):

    send_email(
        to_email,
        "API Approved",
        "Your API has been approved successfully."
    )


# 4. API Rejected

def send_api_rejected_email(to_email: str):

    send_email(
        to_email,
        "API Rejected",
        "Your API has been rejected."
    )


# 5. API Key Generated

def send_api_key_generated_email(to_email: str):

    send_email(
        to_email,
        "API Key Generated",
        "Your API key has been generated successfully."
    )


# 6. API Key Expiring

def send_api_key_expiring_email(to_email: str):

    send_email(
        to_email,
        "API Key Expiring",
        "Your API key is expiring soon."
    )


# 7. Rate Limit Exceeded

def send_rate_limit_exceeded_email(to_email: str):

    send_email(
        to_email,
        "Rate Limit Exceeded",
        "You have exceeded your API rate limit."
    )


# 8. Subscription Cancelled

def send_subscription_cancelled_email(to_email: str):

    send_email(
        to_email,
        "Subscription Cancelled",
        "Your API subscription has been cancelled."
    )