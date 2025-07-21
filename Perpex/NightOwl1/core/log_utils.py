from datetime import datetime

def log_event(message, filepath):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(filepath, "a") as f:
        f.write(f"{timestamp} {message}\n")
