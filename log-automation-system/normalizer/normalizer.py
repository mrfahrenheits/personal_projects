import re
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def normalize_log(line, source):
    """
    Normalize a log line to a standard JSON file
    source: linux, apache, windows
    """

    normalized = {
        'timestamp': None,
        'source': source,
        'event_type': None,
        'ip': None,
        'raw': line
    }

    try:
        if source == 'linux':
            return _normalize_linux(line, normalized)
        
        elif source == 'apache':
            return _normalize_apache(line, normalized)
        
        elif source == 'windows':
            return _normalize_windows(line, normalized)
        
        else:
            logging.warning(f'Unknown Source: {source}')
            return normalized
        
    except Exception as e:
        logging.error(f'Error to normalizing log: {e}')
        return normalized
    
    # ------------------------------
    # Normalizing Linux
    # ------------------------------

    def _normalize_linux(line, normalized):
        # Example:
        # Jan 10 12:45:33 server sshd[1234]: Failed password for root from 192.168.1.10 port 22 ssh2

        # Timestamp
        try:
            ts_match = re.match(r'^[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2}', line)
            if ts_match:
                ts_str = ts_match.group(0)
                normalized['timestamp'] = datetime.strptime(ts_str, '%b %d %H:%M:%S').replace(year=datetime.now().year)

        except:
            pass

        # IP
                