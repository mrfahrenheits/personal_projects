import time
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ApacheLogCollector:
    def __init__(self, filepath, callback=None, interval=1):
        """
        filepath: path to the Apache log file
        callback: function to call when a new log entry is found
        interval: time in seconds to wait between checks
        """
        self.filepath = filepath
        self.callback = callback
        self.interval = interval
        self.position = 0

    def start(self):
        logging.info(f"Starting Apache log collector: {self.filepath}")

        while True:
            if not os.path.exists(self.filepath):
                logging.warning("Log file does not found, waiting...")
                time.sleep(self.interval)
                continue

            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(self.position)
                lines = f.readlines()
                self.position = f.tell()

                for line in lines:
                    if self.callback:
                        try:
                            self.callback(line.strip())
                        except Exception as e:
                            logging.error(f"Error in callback: {e}")

            time.sleep(self.interval)