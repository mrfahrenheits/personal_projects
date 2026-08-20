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

                    # Skip already processed events
                    if last_record and event.RecordNumber <= last_record:
                        continue

                    last_record = event.RecordNumber

                    try:
                        # Extract message safely (works for ALL event types)
                        if hasattr(event, "Strings") and event.Strings:
                            message = " ".join([str(s) for s in event.Strings])
                        else:
                            message = f"Event {event.EventID} (no message)"

                        # Build normalized event dictionary
                        data = {
                            "source": "windows",
                            "event_id": event.EventID,
                            "record_number": event.RecordNumber,
                            "computer": event.ComputerName,
                            "category": event.EventCategory,
                            "time_generated": event.TimeGenerated.Format(),
                            "message": message,
                        }

                        # Send to pipeline
                        if self.callback:
                            try:
                                self.callback(data)
                            except Exception as e:
                                logging.error(f"Error in callback: {e}")

                    except Exception as e:
                        logging.error(f"Failed to normalize Windows event: {e}")            

            time.sleep(self.interval)