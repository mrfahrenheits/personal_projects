from collector.linux_collector import LinuxLogCollector
from normalizer.normalizer import normalize_log
from analyzer.rules_engine import RulesEngine

def alert_handler(alert):
    print(f"[ALERT] {alert}")

engine = RulesEngine(alert_callback=alert_handler)

def process_line(line):
    event = normalize_log(line, source="linux")
    engine.process_event(event)

collector = LinuxLogCollector("/var/log/auth.log", process_line)
collector.start()    