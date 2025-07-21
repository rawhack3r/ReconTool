# NightOwl Configuration Settings

VERSION = "1.0.0"
AUTHOR = "n00bhack3r"
CONTACT = "n00bhack3r@example.com"

# Scan modes
SCAN_MODES = ["light", "deep", "deeper", "custom"]

# Performance Settings
MAX_CONCURRENT_TOOLS = 3
MAX_MEMORY_USAGE = 2048  # MB
MAX_CPU_USAGE = 70  # %

# Path Settings
WORDLIST_DIR = "config/wordlists"
REPORT_DIR = "outputs/reports"
SCAN_OUTPUT_DIR = "outputs/scans"
STATE_FILE = ".nightowl_state"

# UI Settings
UI_REFRESH_RATE = 0.5  # seconds
COLOR_THEME = "dark"  # dark | light | blue

# Notification Settings (optional)
SLACK_WEBHOOK = ""
EMAIL_NOTIFICATIONS = False
EMAIL_RECEIVER = ""

# Feature Toggles
ENABLE_WEB3 = False
ENABLE_DARKWEB = False
ENABLE_CLOUD_SCAN = True