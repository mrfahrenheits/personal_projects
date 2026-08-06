import time
import os
import logging

class LinuxLogCollector:
    def __init__(self, filepath, callback, poll_interval=0.5):
       """
       filepath: log file path (ex: /var/log/auth.log)
       callback: function called for each new line
       poll_interval: interval in secs between verifications
       """
       self.filepath = filepath
       self.callback = callback
       self.poll_interval = poll_interval
       self.position_file = filepath + ".pos"

       logging.basicConfig(
           level=logging.INFO,
           format="%(asctime)s [%(levelname)s] %(message)s"
       ) 

    def _load_last_position(self):
        if os.path.exists(self.position_file):
            try:
                with open(self.position_file, "r") as f:
                    return int(f.read().strip())
            except Exception as e:
                logging.warning(f'Could not read previous position: {e}')
        return 0
    
    def _save_last_position(self, pos):
        try:
            with open(self.position_file, "w") as f:
                f.write(str(pos))
        except Exception as e:
            logging.error(f'Failed to save position: {e}')        

    def _wait_for_file(self):
        while not os.path.exists(self.filepath):
            logging.warning(f'File {self.filepath} not found. Waiting...')
            time.sleep(2)

    def start(self):
        self._wait_for_file()
        last_pos = self._load_last_position()

        logging.info(f'Starting colector for {self.filepath}')
        logging.info(f'Last position: {last_pos}')

        try:
            with open(self.filepath, "r") as f:
                f.seek(last_pos)

            while True:
                line = f.readline()
                if not line:
                    time.sleep(self.poll_interval)
                    continue

                line = line.strip()
                if line:
                    try:
                        self.callback(line)
                    except Exception as e:
                        logging.error(f'Callback error: {e}')    

                last_pos = f.tell()
                self._save_last_position(last_pos)

        except PermissionError:
            logging.error(f'Permision denied reading {self.filepath}. Please run with sudo command')
        except FileNotFoundError:
            logging.error(f'File {self.filepath} not found')
        except Exception as e:
            logging.error(f'Unexpected error in collector: {e}')                                