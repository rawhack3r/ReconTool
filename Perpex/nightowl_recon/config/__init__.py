"""
Configuration package for NightOwl
"""

from .settings import *
from .tool_configs import *
from .patterns import *

__all__ = [
    'BANNER',
    'VERSION',
    'AUTHOR',
    'SCAN_MODES',
    'TOOL_CATEGORIES',
    'WORKFLOW_PHASES',
    'RESOURCE_LIMITS',
    'TIMEOUTS',
    'OUTPUT_FORMATS',
    'LOGGING_CONFIG',
    'API_CONFIGS',
    'UI_CONFIG',
    'SECURITY_CONFIG',
    'OWASP_TOP_10',
    'MANUAL_TESTING_CHECKLIST',
    'IMPORTANT_PATHS',
    'SENSITIVE_EXTENSIONS',
    'SUBDOMAIN_WORDLIST',
    'TOOL_CONFIGS',
    'SECRET_PATTERNS',
    'IMPORTANT_PATTERNS'
]
