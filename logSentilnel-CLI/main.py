from collector.linux_collector import LinuxLogCollector
from normalizer.normalizer import normalize_log
from analyzer.rules_engine import RulesEngine
from storage.jsonl_writer import JSONLWriter
from alerts.alert_manager import AlertManager

writer = JSONLWriter()

alert_manager = AlertManager(
    writer=writer,
    telegram_token=None,  # Replace with your Telegram bot token if needed
    telegram_chat_id=None  # Replace with your Telegram chat ID if needed
)

engine = RulesEngine(alert_callback=alert_manager.handle_alert)

def process_line(line):
    event = normalize_log(line, source="linux")
    writer.write_event(event)
    engine.process_event(event)

collector = LinuxLogCollector("/var/log/auth.log", process_line)
collector.start()    