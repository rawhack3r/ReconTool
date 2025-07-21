# config/settings.py

TOOL_CATEGORIES = {
    "subdomain": ["subfinder", "crtsh", "dnsx"]
}

WORKFLOW_PHASES = {
    "light": [
        {"name": "subdomain", "tools": ["subfinder", "crtsh", "dnsx"]}
    ],
    "deep": [
        {"name": "subdomain", "tools": ["subfinder", "crtsh", "findomain", "dnsx"]}
    ],
    "deepest": [
        {"name": "subdomain", "tools": ["subfinder", "crtsh", "findomain", "dnsx"]}  # <- optionally add Amass here if needed
    ]
}
