import os
import requests
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Discover content and directories on web servers"""
    results = {
        "directories": [],
        "files": [],
        "interesting_paths": []
    }
    
    # Get list of live domains from previous results
    live_domains = _get_live_domains(target)
    
    for domain in live_domains:
        if progress_callback:
            progress_callback("content_discovery", 10, f"Scanning {domain}")
        
        # Check common directories
        for directory in ["admin", "backup", "config", "api", "internal"]:
            url = f"http://{domain}/{directory}"
            if _check_url(url):
                results["directories"].append({
                    "url": url,
                    "status": 200,
                    "domain": domain
                })
        
        # Check common files
        for file in ["robots.txt", "sitemap.xml", ".env", "config.json"]:
            url = f"http://{domain}/{file}"
            if _check_url(url):
                results["files"].append({
                    "url": url,
                    "status": 200,
                    "domain": domain
                })
    
    # Categorize interesting findings
    results["interesting_paths"] = [
        item for item in results["directories"] + results["files"]
        if _is_interesting(item["url"])
    ]
    
    return results

def _get_live_domains(target):
    """Retrieve live domains from previous scan results"""
    # In a real implementation, this would read from the state or output files
    return [f"www.{target}", target]

def _check_url(url):
    """Check if a URL exists"""
    try:
        response = requests.get(url, timeout=5, verify=False)
        return response.status_code == 200
    except:
        return False

def _is_interesting(url):
    """Determine if a path is particularly interesting"""
    interesting_keywords = [
        "admin", "backup", "config", "secret", 
        "api", "internal", "credential", "token"
    ]
    return any(kw in url for kw in interesting_keywords)