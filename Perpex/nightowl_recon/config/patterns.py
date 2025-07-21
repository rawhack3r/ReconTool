"""
Pattern definitions for NightOwl reconnaissance
"""

import re

# Secret patterns for detection
SECRET_PATTERNS = {
    'aws_access_key': {
        'pattern': r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])',
        'description': 'AWS Access Key ID',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'aws_secret_key': {
        'pattern': r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])',
        'description': 'AWS Secret Access Key',
        'severity': 'high',
        'confidence': 'medium'
    },
    
    'jwt_token': {
        'pattern': r'eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
        'description': 'JWT Token',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'api_key': {
        'pattern': r'(?i)(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)["\']?',
        'description': 'Generic API Key',
        'severity': 'medium',
        'confidence': 'medium'
    },
    
    'password': {
        'pattern': r'(?i)(?:password|pwd|pass)["\']?\s*[:=]\s*["\']?([^\s"\']+)["\']?',
        'description': 'Password',
        'severity': 'high',
        'confidence': 'low'
    },
    
    'private_key': {
        'pattern': r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
        'description': 'Private Key',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'slack_token': {
        'pattern': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
        'description': 'Slack Token',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'github_token': {
        'pattern': r'ghp_[0-9a-zA-Z]{36}',
        'description': 'GitHub Personal Access Token',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'google_api': {
        'pattern': r'AIza[0-9A-Za-z-_]{35}',
        'description': 'Google API Key',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'stripe_key': {
        'pattern': r'sk_live_[0-9a-zA-Z]{24}',
        'description': 'Stripe Live Secret Key',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'mailgun_api': {
        'pattern': r'key-[0-9a-zA-Z]{32}',
        'description': 'Mailgun API Key',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'twilio_key': {
        'pattern': r'SK[0-9a-fA-F]{32}',
        'description': 'Twilio API Key',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'paypal_braintree': {
        'pattern': r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
        'description': 'PayPal Braintree Access Token',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'square_oauth': {
        'pattern': r'sq0atp-[0-9A-Za-z-_]{22}',
        'description': 'Square OAuth Secret',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'square_access': {
        'pattern': r'sq0csp-[0-9A-Za-z-_]{43}',
        'description': 'Square Access Token',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'shodan_key': {
        'pattern': r'[a-zA-Z0-9]{32}',
        'description': 'Shodan API Key',
        'severity': 'low',
        'confidence': 'low'
    },
    
    'cert_key': {
        'pattern': r'-----BEGIN CERTIFICATE-----',
        'description': 'Certificate',
        'severity': 'low',
        'confidence': 'high'
    },
    
    'ssh_key': {
        'pattern': r'ssh-rsa [A-Za-z0-9+/]+[=]{0,3}',
        'description': 'SSH Public Key',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'connection_string': {
        'pattern': r'(?i)(jdbc|mysql|postgresql|oracle|sqlserver)://[^\s]+',
        'description': 'Database Connection String',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'ftp_credentials': {
        'pattern': r'ftp://[^\s@]+:[^\s@]+@[^\s]+',
        'description': 'FTP Credentials',
        'severity': 'high',
        'confidence': 'high'
    },
    
    'url_with_auth': {
        'pattern': r'https?://[^\s:@]+:[^\s:@]+@[^\s]+',
        'description': 'URL with Authentication',
        'severity': 'medium',
        'confidence': 'medium'
    },
    
    'base64_key': {
        'pattern': r'(?i)(?:key|secret|token|password)["\']?\s*[:=]\s*["\']?([A-Za-z0-9+/]{20,}={0,2})["\']?',
        'description': 'Base64 Encoded Key',
        'severity': 'medium',
        'confidence': 'low'
    },
    
    'credit_card': {
        'pattern': r'(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})',
        'description': 'Credit Card Number',
        'severity': 'high',
        'confidence': 'medium'
    },
    
    'social_security': {
        'pattern': r'(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}',
        'description': 'Social Security Number',
        'severity': 'high',
        'confidence': 'medium'
    },
    
    'ip_address': {
        'pattern': r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
        'description': 'IP Address',
        'severity': 'low',
        'confidence': 'high'
    },
    
    'internal_ip': {
        'pattern': r'(?:10\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|172\.(?:1[6-9]|2[0-9]|3[0-1])\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|192\.168\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))',
        'description': 'Internal IP Address',
        'severity': 'medium',
        'confidence': 'high'
    },
    
    'email_address': {
        'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'description': 'Email Address',
        'severity': 'low',
        'confidence': 'high'
    },
    
    'domain_name': {
        'pattern': r'(?i)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',
        'description': 'Domain Name',
        'severity': 'low',
        'confidence': 'medium'
    },
    
    'hash_md5': {
        'pattern': r'[a-fA-F0-9]{32}',
        'description': 'MD5 Hash',
        'severity': 'low',
        'confidence': 'low'
    },
    
    'hash_sha1': {
        'pattern': r'[a-fA-F0-9]{40}',
        'description': 'SHA1 Hash',
        'severity': 'low',
        'confidence': 'low'
    },
    
    'hash_sha256': {
        'pattern': r'[a-fA-F0-9]{64}',
        'description': 'SHA256 Hash',
        'severity': 'low',
        'confidence': 'low'
    },
    
    'uuid': {
        'pattern': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
        'description': 'UUID',
        'severity': 'low',
        'confidence': 'high'
    },
    
    'docker_image': {
        'pattern': r'(?i)(?:docker\.io/)?[a-z0-9_-]+/[a-z0-9_-]+(?::[a-z0-9_.-]+)?',
        'description': 'Docker Image',
        'severity': 'low',
        'confidence': 'medium'
    }
}

# Important path patterns
IMPORTANT_PATTERNS = {
    'admin_panels': {
        'patterns': [
            r'/admin',
            r'/administrator',
            r'/admin\.php',
            r'/admincp',
            r'/dashboard',
            r'/panel',
            r'/control',
            r'/manage',
            r'/wp-admin'
        ],
        'description': 'Admin Panel Access',
        'severity': 'high',
        'category': 'access_control'
    },
    
    'authentication': {
        'patterns': [
            r'/login',
            r'/signin',
            r'/auth',
            r'/sso',
            r'/oauth',
            r'/saml'
        ],
        'description': 'Authentication Endpoints',
        'severity': 'medium',
        'category': 'authentication'
    },
    
    'api_endpoints': {
        'patterns': [
            r'/api',
            r'/v\d+',
            r'/graphql',
            r'/swagger',
            r'/docs',
            r'/openapi'
        ],
        'description': 'API Endpoints',
        'severity': 'medium',
        'category': 'api'
    },
    
    'config_files': {
        'patterns': [
            r'/config',
            r'/settings',
            r'/\.env',
            r'/web\.config',
            r'/\.htaccess'
        ],
        'description': 'Configuration Files',
        'severity': 'high',
        'category': 'information_disclosure'
    },
    
    'backup_files': {
        'patterns': [
            r'/backup',
            r'/\.backup',
            r'/\.bak',
            r'/dump',
            r'/\.sql'
        ],
        'description': 'Backup Files',
        'severity': 'high',
        'category': 'information_disclosure'
    },
    
    'development': {
        'patterns': [
            r'/test',
            r'/dev',
            r'/staging',
            r'/debug',
            r'/phpinfo'
        ],
        'description': 'Development Resources',
        'severity': 'medium',
        'category': 'information_disclosure'
    },
    
    'file_operations': {
        'patterns': [
            r'/upload',
            r'/download',
            r'/files',
            r'/attachments',
            r'/media'
        ],
        'description': 'File Operations',
        'severity': 'medium',
        'category': 'file_handling'
    },
    
    'database': {
        'patterns': [
            r'/phpmyadmin',
            r'/adminer',
            r'/mysql',
            r'/database',
            r'/db'
        ],
        'description': 'Database Interfaces',
        'severity': 'high',
        'category': 'database'
    },
    
    'monitoring': {
        'patterns': [
            r'/logs',
            r'/status',
            r'/health',
            r'/metrics',
            r'/monitor'
        ],
        'description': 'Monitoring Endpoints',
        'severity': 'low',
        'category': 'monitoring'
    },
    
    'version_control': {
        'patterns': [
            r'/\.git',
            r'/\.svn',
            r'/\.hg',
            r'/\.bzr'
        ],
        'description': 'Version Control',
        'severity': 'high',
        'category': 'information_disclosure'
    }
}

# Vulnerability patterns
VULNERABILITY_PATTERNS = {
    'xss': {
        'patterns': [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*='
        ],
        'description': 'Cross-Site Scripting (XSS)',
        'severity': 'high',
        'owasp_category': 'A03_2021'
    },
    
    'sql_injection': {
        'patterns': [
            r'union\s+select',
            r'or\s+1\s*=\s*1',
            r'and\s+1\s*=\s*1',
            r'having\s+1\s*=\s*1',
            r'order\s+by\s+\d+'
        ],
        'description': 'SQL Injection',
        'severity': 'high',
        'owasp_category': 'A03_2021'
    },
    
    'command_injection': {
        'patterns': [
            r';\s*ls',
            r';\s*cat',
            r';\s*id',
            r';\s*whoami',
            r'\|\s*nc'
        ],
        'description': 'Command Injection',
        'severity': 'high',
        'owasp_category': 'A03_2021'
    },
    
    'path_traversal': {
        'patterns': [
            r'\.\./\.\.',
            r'\.\.\\\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c'
        ],
        'description': 'Path Traversal',
        'severity': 'high',
        'owasp_category': 'A01_2021'
    },
    
    'ssrf': {
        'patterns': [
            r'127\.0\.0\.1',
            r'localhost',
            r'169\.254\.169\.254',
            r'metadata\.google\.internal'
        ],
        'description': 'Server-Side Request Forgery (SSRF)',
        'severity': 'high',
        'owasp_category': 'A10_2021'
    }
}

# Sensitive information patterns
SENSITIVE_INFO_PATTERNS = {
    'personal_data': {
        'patterns': [
            r'(?i)ssn|social.security',
            r'(?i)driver.license',
            r'(?i)passport',
            r'(?i)national.id'
        ],
        'description': 'Personal Identifiable Information',
        'severity': 'high',
        'category': 'privacy'
    },
    
    'financial_data': {
        'patterns': [
            r'(?i)credit.card',
            r'(?i)bank.account',
            r'(?i)routing.number',
            r'(?i)iban'
        ],
        'description': 'Financial Information',
        'severity': 'high',
        'category': 'financial'
    },
    
    'medical_data': {
        'patterns': [
            r'(?i)medical.record',
            r'(?i)patient.id',
            r'(?i)diagnosis',
            r'(?i)prescription'
        ],
        'description': 'Medical Information',
        'severity': 'high',
        'category': 'healthcare'
    }
}

# Compiled patterns for performance
COMPILED_SECRET_PATTERNS = {
    name: re.compile(pattern['pattern'], re.IGNORECASE | re.MULTILINE)
    for name, pattern in SECRET_PATTERNS.items()
}

COMPILED_IMPORTANT_PATTERNS = {
    category: [re.compile(pattern, re.IGNORECASE) for pattern in patterns['patterns']]
    for category, patterns in IMPORTANT_PATTERNS.items()
}

COMPILED_VULNERABILITY_PATTERNS = {
    name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns['patterns']]
    for name, patterns in VULNERABILITY_PATTERNS.items()
}

# Pattern matching functions
def match_secrets(text):
    """Match secret patterns in text"""
    matches = []
    for name, pattern in COMPILED_SECRET_PATTERNS.items():
        for match in pattern.finditer(text):
            matches.append({
                'type': name,
                'match': match.group(),
                'position': match.span(),
                'severity': SECRET_PATTERNS[name]['severity'],
                'confidence': SECRET_PATTERNS[name]['confidence'],
                'description': SECRET_PATTERNS[name]['description']
            })
    return matches

def match_important_paths(path):
    """Match important path patterns"""
    matches = []
    for category, patterns in COMPILED_IMPORTANT_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(path):
                matches.append({
                    'category': category,
                    'path': path,
                    'severity': IMPORTANT_PATTERNS[category]['severity'],
                    'description': IMPORTANT_PATTERNS[category]['description']
                })
    return matches

def match_vulnerabilities(text):
    """Match vulnerability patterns in text"""
    matches = []
    for name, patterns in COMPILED_VULNERABILITY_PATTERNS.items():
        for pattern in patterns:
            for match in pattern.finditer(text):
                matches.append({
                    'type': name,
                    'match': match.group(),
                    'position': match.span(),
                    'severity': VULNERABILITY_PATTERNS[name]['severity'],
                    'description': VULNERABILITY_PATTERNS[name]['description'],
                    'owasp_category': VULNERABILITY_PATTERNS[name]['owasp_category']
                })
    return matches
