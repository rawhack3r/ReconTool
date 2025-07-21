import requests
import json
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Query crt.sh for subdomains"""
    results = {"subdomains": []}
    try:
        progress_callback("crt_sh", 10, "Querying certificate transparency...")
        url = f"https://crt.sh/?q=%.{target}&output=json"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            progress_callback("crt_sh", 50, f"Processing {len(data)} certificates...")
            
            unique_domains = set()
            for cert in data:
                name_value = cert.get('name_value', '')
                domains = name_value.split('\n')
                for domain in domains:
                    domain = domain.strip().lower()
                    if domain.endswith(f".{target}") and '*' not in domain:
                        unique_domains.add(domain)
            
            results["subdomains"] = [
                {"domain": domain, "source": "crt.sh", "resolved": False}
                for domain in unique_domains
            ]
            
            progress_callback("crt_sh", 90, f"Found {len(unique_domains)} domains")
        else:
            raise Exception(f"API returned {response.status_code}")
            
    except Exception as e:
        ErrorHandler.log_error("crt_sh", str(e), target)
        raise
    
    return results