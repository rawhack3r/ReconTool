"""
Configuration settings for NightOwl Enhanced Reconnaissance Suite
"""

import os
from pathlib import Path

# Banner and metadata
BANNER = """
███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗ ██████╗ ██╗    ██╗██╗     
████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝██╔═══██╗██║    ██║██║     
██╔██╗ ██║██║██║  ███╗███████║   ██║   ██║   ██║██║ █╗ ██║██║     
██║╚██╗██║██║██║   ██║██╔══██║   ██║   ██║   ██║██║███╗██║██║     
██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝███████╗
╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚══════╝
                                                                     
        Enhanced Reconnaissance Suite v2.0
        Advanced AI-Powered Security Testing Platform
"""

VERSION = "2.0.0"
AUTHOR = "n00bhack3r"

# Directories
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = OUTPUT_DIR / "logs"
SCANS_DIR = OUTPUT_DIR / "scans"
REPORTS_DIR = OUTPUT_DIR / "reports"
IMPORTANT_DIR = OUTPUT_DIR / "important"
SECRETS_DIR = OUTPUT_DIR / "secrets"
VULNERABILITIES_DIR = OUTPUT_DIR / "vulnerabilities"

# Scan modes configuration
SCAN_MODES = {
    'light': {
        'description': 'Basic reconnaissance with essential tools',
        'tools': [
            'subfinder', 'crtsh', 'email_extractor', 'alive_checker'
        ],
        'timeout': 300,
        'max_threads': 20,
        'rate_limit': 5
    },
    'deep': {
        'description': 'Comprehensive reconnaissance with all tools',
        'tools': [
            'amass', 'sublist3r', 'assetfinder', 'findomain', 'crtsh', 
            'subfinder', 'chaos', 'email_extractor', 'name_extractor',
            'phone_extractor', 'secret_finder', 'nuclei', 'naabu',
            'httpx', 'owasp_scanner', 'alive_checker', 'important_finder',
            'manual_suggestions'
        ],
        'timeout': 600,
        'max_threads': 50,
        'rate_limit': 10
    },
    'custom': {
        'description': 'User-defined tool selection',
        'tools': [],  # Will be populated by user selection
        'timeout': 300,
        'max_threads': 30,
        'rate_limit': 8
    }
}

# Tool categories
TOOL_CATEGORIES = {
    'subdomain': [
        'amass', 'sublist3r', 'assetfinder', 'findomain', 
        'crtsh', 'subfinder', 'chaos'
    ],
    'information': [
        'email_extractor', 'name_extractor', 'phone_extractor', 'secret_finder'
    ],
    'vulnerability': [
        'nuclei', 'naabu', 'httpx', 'owasp_scanner'
    ],
    'analysis': [
        'alive_checker', 'important_finder', 'manual_suggestions'
    ]
}

# Workflow phases
WORKFLOW_PHASES = {
    'light': [
        {
            'name': 'Basic Subdomain Discovery',
            'tools': ['subfinder', 'crtsh'],
            'description': 'Quick subdomain enumeration using fast sources',
            'parallel': True
        },
        {
            'name': 'Information Extraction',
            'tools': ['email_extractor'],
            'description': 'Extract basic contact information',
            'parallel': False
        },
        {
            'name': 'Alive Check',
            'tools': ['alive_checker'],
            'description': 'Check which domains are responding',
            'parallel': False
        }
    ],
    'deep': [
        {
            'name': 'Comprehensive Subdomain Enumeration',
            'tools': ['amass', 'sublist3r', 'assetfinder', 'findomain', 'crtsh', 'subfinder', 'chaos'],
            'description': 'Thorough subdomain discovery using multiple sources',
            'parallel': True
        },
        {
            'name': 'Information Extraction',
            'tools': ['email_extractor', 'name_extractor', 'phone_extractor'],
            'description': 'Extract emails, names, and phone numbers',
            'parallel': True
        },
        {
            'name': 'Secret Detection',
            'tools': ['secret_finder'],
            'description': 'Find API keys, passwords, and sensitive data',
            'parallel': False
        },
        {
            'name': 'Vulnerability Assessment',
            'tools': ['nuclei', 'naabu', 'httpx', 'owasp_scanner'],
            'description': 'Scan for vulnerabilities and security issues',
            'parallel': True
        },
        {
            'name': 'Asset Analysis',
            'tools': ['alive_checker', 'important_finder'],
            'description': 'Analyze discovered assets and identify important targets',
            'parallel': False
        },
        {
            'name': 'Manual Testing Suggestions',
            'tools': ['manual_suggestions'],
            'description': 'Generate suggestions for manual security testing',
            'parallel': False
        }
    ]
}

# Resource limits
RESOURCE_LIMITS = {
    'max_memory_percent': 85,
    'max_cpu_percent': 80,
    'max_open_files': 1000,
    'max_network_connections': 500,
    'max_concurrent_requests': 100,
    'max_file_size_mb': 100
}

# Timeouts
TIMEOUTS = {
    'tool_execution': 600,
    'http_request': 30,
    'dns_resolution': 10,
    'port_scan': 300,
    'ssl_handshake': 15,
    'connection_timeout': 10
}

# Output formats
OUTPUT_FORMATS = {
    'json': True,
    'csv': True,
    'html': True,
    'txt': True,
    'xml': False,
    'markdown': True
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_handler': True,
    'console_handler': True,
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
    'rotation': 'daily'
}

# API configurations
API_CONFIGS = {
    'shodan': {
        'api_key': os.getenv('SHODAN_API_KEY', ''),
        'base_url': 'https://api.shodan.io',
        'rate_limit': 1,  # requests per second
        'timeout': 30
    },
    'virustotal': {
        'api_key': os.getenv('VIRUSTOTAL_API_KEY', ''),
        'base_url': 'https://www.virustotal.com/api/v3',
        'rate_limit': 4,  # requests per minute
        'timeout': 30
    },
    'chaos': {
        'api_key': os.getenv('CHAOS_API_KEY', ''),
        'base_url': 'https://dns.projectdiscovery.io',
        'rate_limit': 10,  # requests per second
        'timeout': 30
    },
    'securitytrails': {
        'api_key': os.getenv('SECURITYTRAILS_API_KEY', ''),
        'base_url': 'https://api.securitytrails.com/v1',
        'rate_limit': 2,  # requests per second
        'timeout': 30
    },
    'censys': {
        'api_id': os.getenv('CENSYS_API_ID', ''),
        'api_secret': os.getenv('CENSYS_API_SECRET', ''),
        'base_url': 'https://search.censys.io/api',
        'rate_limit': 0.4,  # requests per second
        'timeout': 30
    },
    'binaryedge': {
        'api_key': os.getenv('BINARYEDGE_API_KEY', ''),
        'base_url': 'https://api.binaryedge.io/v2',
        'rate_limit': 1,  # requests per second
        'timeout': 30
    }
}

# UI Configuration
UI_CONFIG = {
    'refresh_rate': 2,  # seconds
    'max_display_items': 100,
    'color_scheme': 'dark',
    'progress_bar_style': 'bar',
    'table_style': 'grid',
    'panel_style': 'rounded',
    'animation_speed': 0.5
}

# Database configuration
DATABASE_CONFIG = {
    'type': 'sqlite',  # sqlite, postgresql, mysql
    'path': OUTPUT_DIR / 'nightowl.db',
    'host': 'localhost',
    'port': 5432,
    'username': '',
    'password': '',
    'database': 'nightowl',
    'pool_size': 10,
    'max_overflow': 20
}

# Security settings
SECURITY_CONFIG = {
    'max_redirects': 5,
    'verify_ssl': True,
    'user_agent': 'NightOwl-Recon/2.0',
    'rate_limit_default': 10,  # requests per second
    'max_concurrent_requests': 100,
    'allowed_protocols': ['http', 'https'],
    'blocked_ips': ['127.0.0.1', '::1'],
    'max_response_size': 50 * 1024 * 1024,  # 50MB
    'request_headers': {
        'User-Agent': 'NightOwl-Recon/2.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
}

# OWASP Top 10 categories
OWASP_TOP_10 = {
    'A01_2021': 'Broken Access Control',
    'A02_2021': 'Cryptographic Failures',
    'A03_2021': 'Injection',
    'A04_2021': 'Insecure Design',
    'A05_2021': 'Security Misconfiguration',
    'A06_2021': 'Vulnerable and Outdated Components',
    'A07_2021': 'Identification and Authentication Failures',
    'A08_2021': 'Software and Data Integrity Failures',
    'A09_2021': 'Security Logging and Monitoring Failures',
    'A10_2021': 'Server-Side Request Forgery'
}

# Manual testing checklist
MANUAL_TESTING_CHECKLIST = {
    'authentication': [
        'Test for default credentials',
        'Check password policy enforcement',
        'Test session management',
        'Verify logout functionality',
        'Test for session fixation',
        'Check for privilege escalation',
        'Test account lockout mechanisms',
        'Verify password reset functionality',
        'Check for username enumeration',
        'Test multi-factor authentication bypass'
    ],
    'authorization': [
        'Test for horizontal privilege escalation',
        'Test for vertical privilege escalation',
        'Check directory traversal',
        'Test for insecure direct object references',
        'Verify access controls',
        'Test for forced browsing',
        'Check administrative interface access',
        'Test role-based access controls',
        'Verify API endpoint authorization',
        'Test for missing function level access control'
    ],
    'input_validation': [
        'Test for SQL injection',
        'Test for XSS vulnerabilities',
        'Check for command injection',
        'Test for file upload vulnerabilities',
        'Check for XXE vulnerabilities',
        'Test for LDAP injection',
        'Check for XPath injection',
        'Test for template injection',
        'Verify input sanitization',
        'Test for buffer overflow'
    ],
    'session_management': [
        'Test session timeout',
        'Check session token entropy',
        'Test for session hijacking',
        'Verify secure cookie attributes',
        'Test concurrent session handling',
        'Check for session fixation',
        'Test session invalidation',
        'Verify CSRF protection',
        'Test for session prediction',
        'Check for session replay attacks'
    ],
    'error_handling': [
        'Test error message disclosure',
        'Check for stack trace exposure',
        'Test for information leakage',
        'Verify custom error pages',
        'Test for debug information exposure',
        'Check for verbose error messages',
        'Test error handling consistency',
        'Verify logging of security events',
        'Test for error-based attacks',
        'Check for timing attacks'
    ],
    'encryption': [
        'Test SSL/TLS configuration',
        'Check for weak encryption',
        'Test for sensitive data exposure',
        'Verify certificate validation',
        'Test for weak cipher suites',
        'Check for SSL/TLS vulnerabilities',
        'Test for man-in-the-middle attacks',
        'Verify key management',
        'Test for downgrade attacks',
        'Check for certificate pinning'
    ],
    'business_logic': [
        'Test workflow bypass',
        'Check for race conditions',
        'Test for logic flaws',
        'Verify business rules enforcement',
        'Test for price manipulation',
        'Check for quantity limits',
        'Test for workflow sequence',
        'Verify transaction integrity',
        'Test for abuse of functionality',
        'Check for resource limits'
    ],
    'api_security': [
        'Test for broken authentication',
        'Check for excessive data exposure',
        'Test for lack of resources & rate limiting',
        'Verify broken function level authorization',
        'Test for mass assignment',
        'Check for security misconfiguration',
        'Test for injection vulnerabilities',
        'Verify improper assets management',
        'Test for insufficient logging & monitoring',
        'Check for API versioning issues'
    ]
}

# Important path patterns
IMPORTANT_PATHS = [
    # Admin panels
    '/admin', '/administrator', '/admin.php', '/admin.html', '/admin.asp', '/admin.aspx',
    '/admincp', '/admin-console', '/admin-panel', '/control-panel', '/cpanel',
    '/dashboard', '/panel', '/control', '/manage', '/manager', '/cp',
    '/wp-admin', '/wp-login.php', '/phpmyadmin', '/myadmin', '/adminer',
    
    # Authentication
    '/login', '/signin', '/sign-in', '/auth', '/authenticate', '/sso',
    '/logout', '/signout', '/sign-out', '/login.php', '/login.html',
    
    # API endpoints
    '/api', '/api/v1', '/api/v2', '/api/v3', '/graphql', '/swagger',
    '/docs', '/documentation', '/openapi', '/spec', '/schema',
    
    # Configuration
    '/config', '/configuration', '/settings', '/setup', '/install',
    '/configure', '/preferences', '/options', '/admin/config',
    
    # Database and backups
    '/backup', '/backups', '/db', '/database', '/sql', '/dump',
    '/export', '/import', '/restore', '/snapshot', '/mysql',
    
    # Development and testing
    '/test', '/testing', '/dev', '/development', '/staging',
    '/debug', '/trace', '/monitor', '/health', '/status',
    
    # File operations
    '/upload', '/uploads', '/files', '/documents', '/attachments',
    '/download', '/downloads', '/media', '/assets', '/static',
    
    # Logs and monitoring
    '/logs', '/log', '/access.log', '/error.log', '/debug.log',
    '/monitoring', '/metrics', '/stats', '/analytics',
    
    # System files
    '/robots.txt', '/sitemap.xml', '/.well-known', '/favicon.ico',
    '/.git', '/.svn', '/.env', '/web.config', '/.htaccess',
    
    # Common directories
    '/www', '/web', '/public', '/private', '/tmp', '/temp',
    '/cache', '/session', '/sessions', '/data', '/var'
]

# Sensitive file extensions
SENSITIVE_EXTENSIONS = [
    # Configuration files
    '.env', '.config', '.ini', '.conf', '.cfg', '.properties',
    '.json', '.xml', '.yml', '.yaml', '.toml', '.plist',
    
    # Database files
    '.sql', '.db', '.sqlite', '.sqlite3', '.mdb', '.accdb',
    '.dbf', '.dump', '.backup', '.bak',
    
    # Log files
    '.log', '.txt', '.csv', '.xls', '.xlsx', '.ods',
    '.tsv', '.out', '.err', '.trace',
    
    # Archive files
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z',
    '.tar.gz', '.tar.bz2', '.tar.xz', '.tgz', '.tbz2',
    
    # Security files
    '.key', '.pem', '.crt', '.cer', '.p12', '.pfx',
    '.jks', '.keystore', '.pub', '.csr',
    
    # Code files
    '.php', '.asp', '.aspx', '.jsp', '.py', '.rb',
    '.pl', '.sh', '.bat', '.cmd', '.ps1',
    
    # Backup files
    '.backup', '.bak', '.old', '.orig', '.tmp', '.temp',
    '.swp', '.swo', '.save', '.copy', '~',
    
    # Documentation
    '.doc', '.docx', '.pdf', '.rtf', '.odt', '.md'
]

# Subdomain wordlist (first 100 most common)
SUBDOMAIN_WORDLIST = [
    'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
    'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'test', 'dev', 'staging',
    'api', 'admin', 'blog', 'shop', 'store', 'news', 'support', 'help', 'mobile',
    'secure', 'vpn', 'ssl', 'cdn', 'static', 'assets', 'images', 'img', 'media',
    'files', 'download', 'downloads', 'uploads', 'backup', 'db', 'database', 'mysql',
    'sql', 'portal', 'dashboard', 'panel', 'control', 'manage', 'login', 'signin',
    'auth', 'sso', 'ldap', 'ad', 'directory', 'hr', 'crm', 'erp', 'finance',
    'accounting', 'internal', 'intranet', 'extranet', 'private', 'public', 'docs',
    'wiki', 'forum', 'community', 'social', 'chat', 'im', 'messenger', 'email',
    'mailbox', 'calendar', 'schedule', 'booking', 'reservation', 'payment', 'billing',
    'invoice', 'checkout', 'cart', 'order', 'orders', 'customer', 'customers',
    'user', 'users', 'member', 'members', 'profile', 'profiles', 'account',
    'accounts', 'settings', 'config', 'configuration', 'preferences', 'options',
    'tools', 'utilities', 'service', 'services', 'resource', 'resources'
]

# Default user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

# Common ports for scanning
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995, 1723, 3306,
    3389, 5432, 5900, 6379, 8080, 8443, 8888, 9000, 9200, 9300, 11211, 27017
]

# HTTP status codes
HTTP_STATUS_CODES = {
    200: 'OK',
    201: 'Created',
    204: 'No Content',
    301: 'Moved Permanently',
    302: 'Found',
    304: 'Not Modified',
    400: 'Bad Request',
    401: 'Unauthorized',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    500: 'Internal Server Error',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout'
}

# Default scan profiles
SCAN_PROFILES = {
    'fast': {
        'timeout': 60,
        'max_threads': 10,
        'tools': ['subfinder', 'crtsh', 'alive_checker']
    },
    'balanced': {
        'timeout': 300,
        'max_threads': 30,
        'tools': ['subfinder', 'crtsh', 'amass', 'email_extractor', 'alive_checker']
    },
    'thorough': {
        'timeout': 600,
        'max_threads': 50,
        'tools': ['amass', 'subfinder', 'sublist3r', 'assetfinder', 'findomain', 
                 'crtsh', 'chaos', 'email_extractor', 'secret_finder', 'nuclei']
    }
}
