import os

def analyze_results(state, output_path):
    summary = f"NightOwl Recon Summary for {state['target']}\n"
    summary += "=" * 50 + "\n\n"
    
    # Subdomains
    if "subdomains" in state:
        summary += f"Subdomains Discovered: {len(state['subdomains'])}\n"
    
    # Live hosts
    if "live_urls" in state:
        summary += f"Live Hosts: {len(state['live_urls'])}\n"
    
    # Vulnerabilities
    if "vulns" in state:
        vuln_count = sum(len(v) for v in state["vulns"].values())
        summary += f"Vulnerabilities Found: {vuln_count}\n"
    
    # Sensitive data
    if "info" in state:
        if "email" in state["info"]:
            summary += f"Emails Found: {len(state['info']['email'])}\n"
        if "pii" in state["info"]:
            summary += f"PII Found: {len(state['info']['pii'])}\n"
    
    # Save to file
    with open(output_path, "w") as f:
        f.write(summary)