# Update core/web_analyzer.py
"""
Web Analysis Module
"""

import os
import json
from core.utils import run_command

# Update discover_services in core/web_analyzer.py
def discover_services(subdomains_file, output_dir):
    """Discover HTTP services"""
    output_file = os.path.join(output_dir, "http_services.txt")
    
    # Check if file exists and has content
    if not os.path.exists(subdomains_file) or os.path.getsize(subdomains_file) == 0:
        return {"file": output_file, "count": 0}
    
    result = run_command(f"httpx -l {subdomains_file} -silent -o {output_file}")
    
    services = []
    if result['success'] and os.path.exists(output_file):
        with open(output_file, 'r') as f:
            services = [line.strip() for line in f if line.strip()]
    
    return {
        "file": output_file,
        "count": len(services)
    }
def content_discovery(services_file, output_dir, config):
    """Discover web content"""
    wordlist = config.get("wordlists", {}).get("directories", "/usr/share/wordlists/dirb/common.txt")
    
    if os.path.exists(services_file):
        with open(services_file, 'r') as f:
            services = f.readlines()
        
        for service in services[:3]:  # Limit for demo
            service = service.strip()
            if service:
                domain = service.split("//")[-1].split("/")[0].replace(":", "_")
                service_dir = os.path.join(output_dir, domain)
                os.makedirs(service_dir, exist_ok=True)
                
                # Directory brute-forcing
                dir_output = os.path.join(service_dir, "directories.txt")
                run_command(f"ffuf -u {service}/FUZZ -w {wordlist} -o {dir_output} -of json")
    return True

def analyze_js(services_file, output_dir):
    """Analyze JavaScript files"""
    js_output = os.path.join(output_dir, "js_analysis")
    os.makedirs(js_output, exist_ok=True)
    
    run_command(f"katana -list {services_file} -jc -kf -o {js_output}/js_files.txt")
    run_command(f"grep -E 'api[_-]?key|secret|token' {js_output}/js_files.txt > {js_output}/secrets.txt")
    
    secrets_count = 0
    if os.path.exists(f"{js_output}/secrets.txt"):
        with open(f"{js_output}/secrets.txt", 'r') as f:
            secrets_count = len(f.readlines())
    
    return {
        "secrets": secrets_count
    }

def github_recon(target, output_dir):
    """GitHub reconnaissance"""
    output_file = os.path.join(output_dir, "github_leaks.txt")
    result = run_command(f"GitHound --target {target} --output {output_file}")
    
    leaks_count = 0
    if result['success'] and os.path.exists(output_file):
        with open(output_file, 'r') as f:
            leaks_count = len(f.readlines())
    
    return {
        "count": leaks_count
    }

def threat_intel(target, output_dir, config):
    """Gather threat intelligence - placeholder"""
    return True

def visual_recon(services_file, output_dir):
    """Capture screenshots"""
    if os.path.exists(services_file):
        run_command(f"gowitness file -s -f {services_file} -d {output_dir}")
    return True