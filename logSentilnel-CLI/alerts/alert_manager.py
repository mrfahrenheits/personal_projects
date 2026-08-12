import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class AlertManager:
    def __init__(self, writer=None, telegram_token=None, telegram_chat_id=None):
        """
        writer: An instance of JSONLWriter to write alerts to a file.
        telegram_token: Telegram bot token for sending alerts via Telegram.
        telegram_chat_id: Telegram chat ID to send alerts to.
        """
        self.writer = writer
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id

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
        self.send_telegram(alert)

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
        logging.error(f"Failed to send alert via Telegram: {e}")