SCAN_MODES = ["light", "deep", "deeper", "custom"]
TARGET_TYPES = ["single", "list", "wildcard"]

TOOL_TIMEOUTS = {
    "amass": 1800,
    "nuclei": 3600,
    "zap": 7200,
    "masscan": 3600
}

MAX_WORKERS = 8
RESUME_ENABLED = True
VERBOSE_OUTPUT = False