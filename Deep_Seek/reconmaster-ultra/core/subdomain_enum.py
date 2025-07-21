# Update core/subdomain_enum.py
"""
Subdomain Enumeration Module
"""

import os
import json
from core.utils import run_command

# Update passive_scan in core/subdomain_enum.py
def passive_scan(target, output_dir, config):
    """Passive subdomain enumeration"""
    output_file = os.path.join(output_dir, "passive.txt")
    
    tools = config.get("tools", {}).get("subdomain", {}).get("passive", ["amass", "subfinder", "assetfinder"])
    results = []
    
    for tool in tools:
        tool_output = f"{output_file}.{tool}"
        if tool == "amass":
            run_command(f"amass enum -passive -d {target} -o {tool_output}")
        elif tool == "subfinder":
            run_command(f"subfinder -d {target} -silent -o {tool_output}")
        elif tool == "assetfinder":
            run_command(f"assetfinder --subs-only {target} > {tool_output}")
        elif tool == "crt.sh":
            # Proper implementation for crt.sh
            run_command(
                f"curl -s 'https://crt.sh/?q=%25.{target}&output=json' | "
                f"jq -r '.[].name_value' | sed 's/\\*\\\.//g' | "
                f"sort -u > {tool_output}"
            )
        
        if os.path.exists(tool_output) and os.path.getsize(tool_output) > 0:
            results.append(tool_output)
    
    # Combine results
    if results:
        run_command(f"cat {' '.join(results)} | sort -u > {output_file}")
    else:
        # Create empty file
        open(output_file, 'a').close()
    
    # Count results
    count = 0
    if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        with open(output_file, 'r') as f:
            count = len(f.readlines())
    
    return {
        "file": output_file,
        "count": count
    }

def active_scan(target, base_file, output_dir, config):
    """Active subdomain brute-forcing"""
    output_file = os.path.join(output_dir, "active.txt")
    wordlist = config.get("wordlists", {}).get("subdomains", "resources/wordlists/subdomains.txt")
    
    run_command(f"puredns bruteforce {wordlist} {target} -r resolvers.txt -q > {output_file}")
    
    # Combine with passive results
    combined_file = os.path.join(output_dir, "all.txt")
    if os.path.exists(base_file) and os.path.exists(output_file):
        run_command(f"cat {base_file} {output_file} | sort -u > {combined_file}")
    elif os.path.exists(output_file):
        run_command(f"cp {output_file} {combined_file}")
    else:
        combined_file = base_file
    
    # Count results
    count = 0
    if os.path.exists(combined_file):
        with open(combined_file, 'r') as f:
            count = len(f.readlines())
    
    return {
        "file": combined_file,
        "count": count
    }