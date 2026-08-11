import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class JSONLWriter:
    def __init__(self, events_path="data/events.jsonl", alerts_path="data/alerts.jsonl"):
        self.events_path = events_path
        self.alerts_path = alerts_path

        # Ensure the directories exist
        os.makedirs(os.path.dirname(events_path), exist_ok=True)
        os.makedirs(os.path.dirname(alerts_path), exist_ok=True)

    def write_event(self, event: dict):
        # Write a normalized event to the events.jsonl file
        try:
            with open(self.events_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logging.error(f"Failed to write event: {e}")

    def write_alert(self, alert: dict):
        # Write an alert to the alerts.jsonl file
        try:
            with open(self.alerts_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert) + "\n")
        except Exception as e:
            logging.error(f"Failed to write alert: {e}")