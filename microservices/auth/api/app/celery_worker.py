import smtplib
from email.mime.text import MIMEText

from celery import Celery
import os

celery = Celery(
    'worker',
    broker=os.environ.get("CELERY_BROKER_URL"),
    backend=os.environ.get("CELERY_RESULT_BACKEND"),
)

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def send_activation_email(self, email: str, activation_link: str):
    """Sends an activation e-mail with retry and Celery SLA."""
    try:
        from_email = os.environ["MAIL_FROM"]
        msg = MIMEText(f"Activate your account: {activation_link}", "plain", "utf-8")
        msg["Subject"] = "Account activation"
        msg["From"] = from_email
        msg["To"] = email
        with smtplib.SMTP(os.environ["SMTP_HOST"], 587) as s:
            s.starttls()
            s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
            s.sendmail(from_email, [email], msg.as_string())
    except Exception as exc:
        raise self.retry(exc=exc)