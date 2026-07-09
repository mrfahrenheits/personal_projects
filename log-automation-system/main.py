from collector.linux_collector import LinuxLogCollector
from normalizer.normalizer import normalize_log

def process_line(line):
    # print(f'[LOG] {line}')
    normalized = normalize_log(line, source="linux")
    print(normalized)

# if __namẹ__ == "__main__":
collector = LinuxLogCollector("/var/log/auth.log", process_line)
collector.start()    