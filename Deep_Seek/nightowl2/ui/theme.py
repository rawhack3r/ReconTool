from rich.theme import Theme

NIGHTOWL_THEME = Theme({
    # UI Elements
    "banner": "bold #00FFFF",               # Cyan
    "subtitle": "#00FF99",                  # Green
    "header": "bold #0077FF on #0A0A2A",    # Deep blue
    "panel": "#1A1A4A",                     # Dark blue
    
    # Status Indicators
    "success": "bold #00FF00",              # Bright green
    "warning": "bold #FFFF00",              # Yellow
    "error": "bold #FF0055",                # Pink
    "skipped": "#5555FF",                   # Light blue
    
    # Workflow
    "phase_header": "bold #FF7700",         # Orange
    "phase_active": "bold #00FF88",         # Bright green
    "phase_completed": "#00AA55",           # Dark green
    "phase_pending": "#5555FF",             # Blue
    
    # Tools
    "tool_name": "bold #00FFFF",            # Cyan
    "description": "#AAAAFF",               # Lavender
    "progress": "#00FF99",                  # Green
    
    # Results
    "count": "bold #FFDD00",                # Gold
    "vuln_critical": "bold #FF0055",        # Pink
    "vuln_high": "bold #FF5500",            # Orange
    "vuln_medium": "bold #FFAA00",          # Yellow
    "vuln_low": "bold #00AAFF",             # Light blue
    
    # Special
    "important": "bold #FF00FF",            # Magenta
    "secret": "bold #FF0055 on #FFFF00",    # Pink on yellow
    "ai": "bold #AA00FF"                    # Purple
})