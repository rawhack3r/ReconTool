# Update core/port_scanner.py
"""
Port Scanner Module
"""

import os
import json
from core.utils import run_command

def run(subdomains_file, output_dir, mode="default"):
    """Perform port scanning based on mode"""
    output_file = os.path.join(output_dir, "port_scan.json")
    
    if mode == "lightning":
        cmd = f"naabu -list {subdomains_file} -top-ports 100 -json -o {output_file}"
    elif mode == "default":
        cmd = f"naabu -list {subdomains_file} -p 0-10000 -json -o {output_file}"
    else:  # deep or assassin
        cmd = f"nmap -iL {subdomains_file} -T4 -A -oX {output_file}.xml"
    
    result = run_command(cmd)
    
    # Count open ports
    count = 0
    if result['success']:
        if "naabu" in cmd and os.path.exists(output_file):
            with open(output_file, 'r') as f:
                count = sum(1 for line in f)
        elif os.path.exists(f"{output_file}.xml"):
            # Simple XML parsing for demo
            with open(f"{output_file}.xml", 'r') as f:
                count = f.read().count("<port protocol")
    
    return {
        "file": output_file,
        "count": count
    }