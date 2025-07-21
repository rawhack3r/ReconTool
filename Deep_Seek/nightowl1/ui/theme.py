from rich.theme import Theme

NIGHTOWL_THEME = Theme({
    # UI Elements
    "banner": "bold #6A0DAD",
    "subtitle": "#8E44AD",
    "header": "bold #3498DB on #2C3E50",
    "resource_panel": "#1ABC9C",
    
    # Status Indicators
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "skipped": "dim italic",
    
    # Workflow
    "phase_header": "bold #F39C12",
    "phase_active": "bold #2ECC71",
    "phase_completed": "dim #27AE60",
    "phase_pending": "dim #7F8C8D",
    
    # Tools
    "tool_name": "bold #3498DB",
    "description": "#BDC3C7",
    "progress": "#1ABC9C",
    
    # Results
    "count": "bold #F1C40F",
    "vuln_critical": "bold red",
    "vuln_high": "bold #E74C3C",
    "vuln_medium": "bold #F39C12",
    "vuln_low": "bold #3498DB",
    
    # Special
    "important": "bold blink #FF00FF",
    "secret": "bold #FF0000 on #FFFF00"
})