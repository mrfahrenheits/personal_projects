import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class AlertManager:
    def __init__(
    self, 
    writer=None, 
    telegram_token=None, 
    telegram_chat_id=None,
    smtp_server=None,
    smtp_port=None,
    smtp_user=None,
    smtp_password=None,
    email_to=None
):
        """
        writer: An instance of JSONLWriter to write alerts to a file.
        telegram_token / telegram_chat_id: Telegram bot token and chat ID for sending alerts via Telegram.
        smtp_*: Email configuration
        email_to: Recipient email address for sending alerts via email.
        """
        self.writer = writer

        # Telegram
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id

        # Email
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_to = email_to

# ---------------------------------------------------------
# Main entry
# ---------------------------------------------------------

    def handle_alert(self, alert: dict):
        # Receives an alert from analyzer and run actions
        logging.warning(f"[ALERT] {alert['title']} | IP: {alert['ip']}")

        # 1) Write an alert in a JSONL file
        if self.writer:
            self.writer.write_alert(alert)

        # 2) Send an alert via Telegram (optional)
        if self.telegram_token and self.telegram_chat_id:
            self._send_telegram(alert)

        # 3) Send an alert via email (optional)
        if self.smtp_server and self.smtp_user and self.email_to:
            self._send_email(alert)

# ---------------------------------------------------------
# Send alert via Telegram
# ---------------------------------------------------------
    def _send_telegram(self, alert):
        try:
            message = (
                f"🚨 *Security Alert*\n"
                f"*Title:* {alert['title']}\n"
                f"*IP:* {alert['ip']}\n"
                f"*Count:* {alert['count']}\n"
                f"*Rule:* {alert['rule']}\n"
            )

            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

            requests.post(url, data={
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            })

            logging.info("Alert sent via Telegram to chat ID.")

        except Exception as e:
            logging.error(f"Failed to send alert by Telegram: {e}")

# ---------------------------------------------------------
# Send an alert via email
# ---------------------------------------------------------
    def _send_email(self, alert):
        try:
            subject = f"Security Alert: {alert['title']}"
            body = (
                f"Security Alert\n\n"
                f"Title: {alert['title']}\n"
                f"IP: {alert['ip']}\n"
                f"Count: {alert['count']}\n"
                f"Rule: {alert['rule']}\n"
            )

            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = self.email_to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logging.info("Alert sent by email")

        except Exception as e:
            logging.error(f"Failed to send alert by email: {e}")