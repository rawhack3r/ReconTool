SCAN_MODES = ["light", "deep", "deeper", "custom"]
TARGET_TYPES = ["single", "list", "wildcard"]

TOOL_TIMEOUTS = {
    "amass": 1200,
    "nuclei": 1800,
    "cloud_scanner": 900
}

MAX_WORKERS = 8

CHECKPOINT_INTERVAL = 300
MAX_CPU = 0.8
MAX_MEMORY = 0.8

OUTPUT_DIRS = [
    "important",
    "vulnerabilities",
    "cloud",
    "api_security",
    "threat_intel",
    "ai_insights",
    "attack_surface",
    "blockchain",
    "reports",
    "state_exports",
    "errors"
]

AI_MODELS = {
    "vulnerability_analysis": "gpt-4",
    "secret_classification": "distilbert-base-uncased",
    "attack_modeling": "gpt-4"
}