import time
import logging
import win32evtlog

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class WindowsEventLogCollector:
    def __init__(self, log_name="Security", callback=None, interval=2):
        """
        log_name: Security, System, Application
        callback: function to call when a new event is found
        interval: time in seconds to wait between checks
        """
        self.log_name = log_name
        self.callback = callback
        self.interval = interval

    def start(self):
        logging.info(f"Starting Windows collector ({self.log_name})")

        server = 'localhost'
        hand = win32evtlog.OpenEventLog(server, self.log_name)

        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        last_record = None

        while True:
            events = win32evtlog.ReadEventLog(hand, flags, 0)

            if events:
                for event in reversed(events):
                    if last_record and event.RecordNumber <= last_record:
                        continue

                    last_record = event.RecordNumber

                    if self.callback:
                        try:
                            self.callback(event)
                        except Exception as e:
                            logging.error(f"Error in callback: {e}")

            time.sleep(self.interval)