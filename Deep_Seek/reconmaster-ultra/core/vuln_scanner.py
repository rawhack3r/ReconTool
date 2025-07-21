# Update core/vuln_scanner.py
"""
Vulnerability Scanner Module
"""

import os
import json
from core.utils import run_command

def run(services_file, output_dir, mode="default"):
    """Run vulnerability scanning"""
    output_file = os.path.join(output_dir, "nuclei_results.json")
    
    # Determine templates based on mode
    if mode == "lightning":
        templates = "-t cves/"
    elif mode == "default":
        templates = "-t cves/ -t vulnerabilities/"
    else:  # deep or assassin
        templates = ""
    
    if os.path.exists(services_file):
        result = run_command(f"nuclei -l {services_file} {templates} -severity critical,high -json -o {output_file}")
    else:
        return {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    # Parse results
    critical = 0
    high = 0
    medium = 0
    low = 0
    
    if result['success'] and os.path.exists(output_file):
        with open(output_file, 'r') as f:
            for line in f:
                try:
                    vuln = json.loads(line)
                    severity = vuln.get("info", {}).get("severity", "").lower()
                    if severity == "critical":
                        critical += 1
                    elif severity == "high":
                        high += 1
                    elif severity == "medium":
                        medium += 1
                    elif severity == "low":
                        low += 1
                except json.JSONDecodeError:
                    continue
    
    return {
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }