"""
Tool-specific configurations for NightOwl
"""

# Tool configurations
TOOL_CONFIGS = {
    'amass': {
        'binary': 'amass',
        'args': ['enum', '-d', '{target}', '-json', '-timeout', '{timeout}'],
        'output_format': 'json',
        'rate_limit': 10,
        'timeout': 600,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'subfinder': {
        'binary': 'subfinder',
        'args': ['-d', '{target}', '-silent', '-json', '-timeout', '{timeout}'],
        'output_format': 'json',
        'rate_limit': 50,
        'timeout': 300,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'sublist3r': {
        'binary': 'python3',
        'args': ['-m', 'sublist3r', '-d', '{target}', '-o', '{output}'],
        'output_format': 'file',
        'rate_limit': 5,
        'timeout': 300,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'assetfinder': {
        'binary': 'assetfinder',
        'args': ['-subs-only', '{target}'],
        'output_format': 'text',
        'rate_limit': 20,
        'timeout': 180,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'findomain': {
        'binary': 'findomain',
        'args': ['-t', '{target}', '-q', '-u'],
        'output_format': 'text',
        'rate_limit': 15,
        'timeout': 240,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'chaos': {
        'binary': None,  # API-based
        'api_endpoint': 'https://dns.projectdiscovery.io/dns/{target}/subdomains',
        'output_format': 'json',
        'rate_limit': 10,
        'timeout': 60,
        'requires_api_key': True,
        'api_key_env': 'CHAOS_API_KEY',
        'parallel_safe': True
    },
    
    'crtsh': {
        'binary': None,  # API-based
        'api_endpoint': 'https://crt.sh/?q={target}&output=json',
        'output_format': 'json',
        'rate_limit': 5,
        'timeout': 30,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'nuclei': {
        'binary': 'nuclei',
        'args': ['-u', '{target}', '-json', '-silent', '-timeout', '{timeout}'],
        'output_format': 'json',
        'rate_limit': 10,
        'timeout': 300,
        'requires_api_key': False,
        'parallel_safe': False
    },
    
    'naabu': {
        'binary': 'naabu',
        'args': ['-host', '{target}', '-json', '-silent', '-timeout', '{timeout}'],
        'output_format': 'json',
        'rate_limit': 100,
        'timeout': 120,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'httpx': {
        'binary': 'httpx',
        'args': ['-u', '{target}', '-json', '-silent', '-timeout', '{timeout}'],
        'output_format': 'json',
        'rate_limit': 20,
        'timeout': 60,
        'requires_api_key': False,
        'parallel_safe': True
    },
    
    'shodan': {
        'binary': None,  # API-based
        'api_endpoint': 'https://api.shodan.io/shodan/host/{target}',
        'output_format': 'json',
        'rate_limit': 1,
        'timeout': 30,
        'requires_api_key': True,
        'api_key_env': 'SHODAN_API_KEY',
        'parallel_safe': True
    },
    
    'virustotal': {
        'binary': None,  # API-based
        'api_endpoint': 'https://www.virustotal.com/api/v3/domains/{target}',
        'output_format': 'json',
        'rate_limit': 4,  # per minute
        'timeout': 30,
        'requires_api_key': True,
        'api_key_env': 'VIRUSTOTAL_API_KEY',
        'parallel_safe': True
    }
}

# Tool installation commands
TOOL_INSTALL_COMMANDS = {
    'amass': 'go install github.com/OWASP/Amass/v3/...@latest',
    'subfinder': 'go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest',
    'assetfinder': 'go install github.com/tomnomnom/assetfinder@latest',
    'findomain': 'wget https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux && chmod +x findomain-linux && sudo mv findomain-linux /usr/local/bin/findomain',
    'nuclei': 'go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest',
    'naabu': 'go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest',
    'httpx': 'go install github.com/projectdiscovery/httpx/cmd/httpx@latest',
    'sublist3r': 'pip3 install sublist3r',
    'chaos': 'API-based tool, requires API key from ProjectDiscovery'
}

# Tool descriptions
TOOL_DESCRIPTIONS = {
    'amass': 'In-depth Attack Surface Mapping and Asset Discovery',
    'subfinder': 'Fast subdomain discovery tool',
    'sublist3r': 'Python tool for subdomain enumeration',
    'assetfinder': 'Find domains and subdomains potentially related to a given domain',
    'findomain': 'Fast and cross-platform subdomain enumerator',
    'crtsh': 'Certificate transparency logs subdomain finder',
    'chaos': 'ProjectDiscovery DNS data API',
    'nuclei': 'Fast and customizable vulnerability scanner',
    'naabu': 'Fast port scanner written in Go',
    'httpx': 'Fast and multi-purpose HTTP toolkit',
    'email_extractor': 'Extract email addresses from web pages',
    'name_extractor': 'Extract person names from web content',
    'phone_extractor': 'Extract phone numbers from web content',
    'secret_finder': 'Find API keys, passwords, and sensitive data',
    'alive_checker': 'Check if discovered domains are alive',
    'important_finder': 'Identify important assets and paths',
    'manual_suggestions': 'Generate manual testing recommendations',
    'owasp_scanner': 'OWASP Top 10 vulnerability scanner'
}

# Tool categories and priorities
TOOL_PRIORITIES = {
    'high': ['amass', 'subfinder', 'nuclei', 'httpx'],
    'medium': ['sublist3r', 'assetfinder', 'findomain', 'naabu'],
    'low': ['crtsh', 'chaos', 'email_extractor', 'secret_finder']
}

# Default tool parameters
DEFAULT_TOOL_PARAMS = {
    'timeout': 300,
    'max_retries': 3,
    'retry_delay': 5,
    'rate_limit': 10,
    'user_agent': 'NightOwl-Recon/2.0',
    'max_redirects': 5,
    'verify_ssl': True
}

# Tool output parsers
TOOL_OUTPUT_PARSERS = {
    'amass': 'json',
    'subfinder': 'json',
    'sublist3r': 'file',
    'assetfinder': 'text',
    'findomain': 'text',
    'crtsh': 'json',
    'chaos': 'json',
    'nuclei': 'json',
    'naabu': 'json',
    'httpx': 'json'
}

# Tool error patterns
TOOL_ERROR_PATTERNS = {
    'amass': [
        'error',
        'failed',
        'timeout',
        'connection refused',
        'no such host'
    ],
    'subfinder': [
        'error',
        'failed',
        'could not resolve',
        'timeout'
    ],
    'nuclei': [
        'error',
        'failed',
        'template not found',
        'connection refused'
    ]
}

# Tool success indicators
TOOL_SUCCESS_PATTERNS = {
    'amass': ['name', 'domain', 'addr'],
    'subfinder': ['host', 'subdomain'],
    'nuclei': ['template-id', 'info', 'matched-at'],
    'naabu': ['host', 'port', 'ip'],
    'httpx': ['url', 'status-code', 'content-length']
}
