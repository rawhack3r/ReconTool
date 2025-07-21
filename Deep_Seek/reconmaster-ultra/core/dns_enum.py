# Update core/dns_enum.py
"""
DNS Enumeration Module
"""

import os
import json
from core.utils import run_command

def run(target, output_dir):
    """Perform DNS enumeration"""
    results = {
        "subdomains": 0,
        "records": {}
    }
    
    # WHOIS lookup
    whois_file = os.path.join(output_dir, "whois.txt")
    run_command(f"whois {target} > {whois_file}")
    
    # DNS records
    dns_file = os.path.join(output_dir, "dns_records.txt")
    run_command(f"dig {target} ANY +noall +answer > {dns_file}")
    
    # Subdomain enumeration via DNS
    dns_subs_file = os.path.join(output_dir, "dns_subs.txt")
    run_command(f"subfinder -d {target} -silent > {dns_subs_file}")
    
    # Count subdomains
    if os.path.exists(dns_subs_file):
        with open(dns_subs_file, 'r') as f:
            subdomains = f.readlines()
            results["subdomains"] = len(subdomains)
    
    return results