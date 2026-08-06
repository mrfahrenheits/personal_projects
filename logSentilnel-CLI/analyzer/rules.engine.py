import time
import logging
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class RulesEngine:
    def __init__(self, alert_callback=None):
        """
        alert_callback: function call for triggering rules
        """
        self.alert_callback = alert_callback

        # IP event counter 
        self.failed_logins = defaultdict(list) # {ip: [timestamps]}
        self.http_errors = defaultdict(list)   # {ip: [timestamps]}

        # Rules configurations
        self.login_fail_threshold = 5    # fails permited
        self.login_fail_windows = 60     # seconds

    # -------------------------------------------------------------
    # Analyzer main entry
    # -------------------------------------------------------------
    def process_event(self, event):
        """
        event: normalized JSON from normalizer
        """

        source = event.get("source")
        event_type = event.get("event_type")
        ip = event.get("ip")
        timestamp = event.get("timestamp")

        if not timestamp:
            return    # skip analysis without timestamp
        
        # RUles by log type
        if source == "linux":
            self._analyze_linux(event_type, ip, timestamp)
        
        elif source == "apache":
            self._analyze_apache(event_type, ip, timestamp)

        elif source == "windows":
            self._analyze_windows(event_type, ip, timestamp)

    # -------------------------------------------------------------
    # Apache rules
    # -------------------------------------------------------------        
    def _analyze_apache(self, event_type, ip, timestamp):
        if event_type in ["not_found", "server_error"] and ip:
            self.http_errors[ip].append(timestamp)
            self._check_login_fail_rule(ip)

    # -------------------------------------------------------------
    # Windows rules
    # -------------------------------------------------------------
    def _analyze_windows(self, event_type, ip, timestamp):
        if event_type == "login_failed" and ip:
            self.failed_logins[ip].append(timestamp)
            self._check_login_fail_rule(ip)

    # -------------------------------------------------------------
    # Linux rules
    # -------------------------------------------------------------       
    def _analyze_linux(self, event_type, ip, timestamp):
        if event_type == "login_failed" and ip:
            self.failed_logins[ip].append(timestamp)
            self._check_login_fail_rule(ip)
    
    # -------------------------------------------------------------
    # Rule: Multiple login failures
    # -------------------------------------------------------------
    def _check_login_fail_rule(self, ip):
        timestamps = self.failed_logins[ip]
        now = time.time()

        # Keep only events inside a window
        timestamps = [t for t in timestamps if now - t.timestamp() <= self.login_fail_window]
        self.failed_logins[ip] = timestamps

        if len(timestamps) >= self.login_fail_threshold:
            self._trigger_alert(
                title="Multiple logins failures detected",
                ip=ip,
                count=len(timestamps),
                rule="login_fail"
            )

    # -------------------------------------------------------------
    # Rule: Multiple HTTP errors
    # -------------------------------------------------------------
    def _check_http_error_rule(self, ip):
        timestamps =self.http_errors[ip]
        now = time.time()

        timestamps = [t for t in timestamps if now - t.timestamp() <= self.http_error_window]
        self.http_errors[ip] = timestamps

        if len(timestamps) >= self.http_error_threshold:
            self._trigger_alert(
                title="Excessive HTTP errors logged",
                ip=ip,
                count=len(timestamps),
                rule="http_error"
            )

    # -------------------------------------------------------------
    # Alert trigger
    # -------------------------------------------------------------
    def _trigger_alert(self, title, ip, count, rule):
        alert = {
            "title": title,
            "ip": ip,
            "count": count,
            "rule": rule,
            "timestamp": time.time()
        }

        logging.warning(f"[ALERT] {title} | IP: {ip} | Instances: {count}")

        if self.alert_callback:
            try:
                self.alert_callback(alert)
            except Exception as e:
                logging.error(f"Alert delivery failed: {e}")