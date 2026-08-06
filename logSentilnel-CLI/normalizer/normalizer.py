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
# Normalizing for Linux
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
    ip_match = re.search(r"(\d{1,3}\.){3}\d{1,3}", line)
    if ip_match:
        normalized["ip"] = ip_match.group(0)

    # Event type
    if "Failed password" in line:
        normalized["event_type"] = "login_failed"
    elif "Accepted password" in line:
        normalized["event_type"] = "login_sucess"
    elif "error" in line.lower():
        normalized["event_type"] = "error"
    else:
        normalized["event_type"] = "other"

    return normalized
    
# ------------------------------
# Normalizing for Apache
# ------------------------------

def _normalize_apache(line, normalized):
    # Example:
    # 192.168.1.10 - - [10/Jan/2024:12:45:33 +0000] "GET /index.html HTTP/1.1" 200 532

    # IP
    ip_match = re.match(r"(\d{1,3}\.){3}\d{1,3}", line)
    if ip_match:
        normalized["ip"] = ip_match.group(0)
        
    # Timestamp
    ts_match = re.search(r"\[(.*?)\]", line)

    if ts_match:
        ts_str = ts_match.group(1)
        try:
            normalized["timestamp"] = datetime.strptime(ts_str, "%d/%b/%Y:%H:%M:%S %z")
        except:
            pass

    # Event type
    if " 404 " in line:
        normalized["event_type"] = "not_found"
    elif " 500 " in line:
        normalized["event_type"] = "server_error"
    else:
        normalized["event_type"] = "http_request"

    return normalized

# ------------------------------
# Normalizing for Windows
# ------------------------------

def _normalize_windows(line, normalized):
    # Assuming Windows collector converted EVTX to text
    # Example:
    # EventID: 4625 | TimeCreated: 2024-01-10 12:45:33 | Message: An account failed to log on | IP: 192.168.1.10

    # Timestamp
    ts_match = re.search(r"TimeCreated:\s*(.*?)\s*\|", line)
    if ts_match:
        try:
            normalized["timestamp"] = datetime.strptime(ts_match.group(1), "%Y-%m-%d %H:%M:%S")
        except:
            pass

    # IP
    ip_match = re.search(r"IP:\s*((\d{1,3}\.){3}\d{1,3})", line)
    if ip_match:
        normalized["ip"] = ip_match.group(1)

    # Event type
    if "failed to log on" in line.lower():
        normalized["event_type"] = "login_failed"
    elif "logon" in line.lower():
        normalized["event_type"] = "login_sucess"
    else:
        normalized["event_type"] = "other"

    return normalized    