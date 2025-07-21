import re
from pathlib import Path

def validate_target(target):
    # Basic domain regex; extend for full validation if needed
    return bool(re.match(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.[A-Za-z]{2,6}$", target)) or Path(target).is_file()

def setup_directories(output):
    dirs = [
        Path(output) / d for d in ("scans", "reports", "important", "secrets", "vulnerabilities", "logs")
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

def check_dependencies():
    # Sample tool check; expand as needed
    results = {}
    try:
        import rich
        results["rich"] = {"available": True, "version": rich.__version__}
    except ImportError:
        results["rich"] = {"available": False, "error": "Not installed"}
    # Add more tools here
    return results

def get_current_timestamp():
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"

def format_duration(seconds):
    mins, sec = divmod(int(seconds), 60)
    return f"{mins}m{sec}s" if mins else f"{sec}s"
