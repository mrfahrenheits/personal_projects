from collector.linux_collector import LinuxLogCollector
from normalizer.normalizer import normalize_log
from analyzer.rules_engine import RulesEngine
from storage.jsonl_writer import JSONLWriter

writer = JSONLWriter()

def alert_handler(alert):
    writer.write_alert(alert)

engine = RulesEngine(alert_callback=alert_handler)

def process_line(line):
    event = normalize_log(line, source="linux")
    writer.write_event(event)
    engine.process_event(event)

collector = LinuxLogCollector("/var/log/auth.log", process_line)
collector.start()    