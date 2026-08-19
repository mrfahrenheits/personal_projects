import threading
import logging
import yaml

from collector.linux_collector import LinuxLogCollector
from collector.windows_collector import WindowsEventLogCollector
from collector.apache_collector import ApacheLogCollector

from normalizer.normalizer import normalize_log
from analyzer.rules_engine import RulesEngine
from alerts.alert_manager import AlertManager
from storage.jsonl_writer import JSONLWriter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------
# Loading configuration
# ---------------------------------------------------------

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()

# ---------------------------------------------------------
# Starting main modules
# ---------------------------------------------------------

writer = JSONLWriter(
    events_path=config["storage"]["events_path"],
    alerts_path=config["storage"]["alerts_path"]
)

alert_manager = AlertManager(
    writer=writer,

    # Telegram
    telegram_token=config["alerts"]["telegram"]["token"],
    telegram_chat_id=config["alerts"]["telegram"]["chat_id"],

    # Email
    smtp_server=config["alerts"]["email"]["smtp_server"],
    smtp_port=config["alerts"]["email"]["smtp_port"],
    smtp_user=config["alerts"]["email"]["smtp_user"],
    smtp_password=config["alerts"]["email"]["smtp_password"],
    email_to=config["alerts"]["email"]["email_to"]
)

engine = RulesEngine(alert_callback=alert_manager.handle_alert)

# ---------------------------------------------------------
# Common processing function
# ---------------------------------------------------------

def process_event(line, source):
    try:
        event = normalize_log(line, source)
        writer.write_event(event)
        engine.process_event(event)
    except Exception as e:
        logging.error(f"Error processing event: {e}")

# ---------------------------------------------------------
# Starting collectors
# ---------------------------------------------------------

threads = []

# Linux
if config["collectors"]["linux"]["enabled"]:
    linux_path = config["collectors"]["linux"]["filepath"]
    linux_collector = LinuxLogCollector(
        filepath=linux_path,
        callback=lambda line: process_event(line, "linux")
    )
    threads.append(threading.Thread(target=linux_collector.start))

# Windows
if config["collectors"]["windows"]["enabled"]:
    windows_log = config["collectors"]["windows"]["log_name"]
    windows_collector = WindowsEventLogCollector(
        log_name=windows_log,
        callback=lambda evt: process_event(evt, "windows")
    )
    threads.append(threading.Thread(target=windows_collector.start))

# Apache
if config["collectors"]["apache"]["enabled"]:
    apache_path = config["collectors"]["apache"]["filepath"]
    apache_collector = ApacheLogCollector(
        filepath=apache_path,
        callback=lambda line: process_event(line, "apache")
    )
    threads.append(threading.Thread(target=apache_collector.start))

# ---------------------------------------------------------
# Start all collectors
# ---------------------------------------------------------

logging.info("Starting collectors...")

for t in threads:
    t.daemon = True
    t.start()

logging.info("All collectors are running.")

# ---------------------------------------------------------
# Keep the main thread alive
# ---------------------------------------------------------

try:
    while True:
        pass
except KeyboardInterrupt:
    logging.info("Shutting down LogSentinel-CLI...") 