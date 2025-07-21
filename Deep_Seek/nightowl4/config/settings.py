import os

# Redis configuration for distributed scanning
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# API configuration
API_HOST = "0.0.0.0"
API_PORT = 8000

# Default scan modes
SCAN_MODES = {
    "light": ["assetfinder", "sublist3r", "crt_sh"],
    "deep": ["amass", "subfinder", "findomain", "dirsearch", "ffuf", "wayback", "nuclei"],
    "deeper": ["amass", "subfinder", "findomain", "crt_sh", "chaos", "dnsrecon", 
               "dirsearch", "ffuf", "gospider", "wayback", "gau", "hakrawler", 
               "email", "secret", "pii", "nuclei", "zap", "wpscan", "testssl"]
}

# Default wordlists
WORDLISTS = {
    "directories": "config/wordlists/directories.txt",
    "subdomains": "config/wordlists/subdomains.txt",
    "parameters": "config/wordlists/parameters.txt"
}

# Output directories
OUTPUT_DIRS = [
    "subdomains",
    "live_hosts",
    "content",
    "info",
    "vulns",
    "reports",
    "network",
    "mobile"
]