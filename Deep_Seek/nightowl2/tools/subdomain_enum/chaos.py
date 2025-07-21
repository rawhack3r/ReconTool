import requests
import json
from core.error_handler import ErrorHandler

def run_chaos(target):
    """Query Chaos dataset for subdomains"""
    try:
        url = f"https://chaos-data.projectdiscovery.io/{target}.txt"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        subdomains = set()
        for line in response.text.splitlines():
            if line.strip() and not line.startswith("#"):
                subdomains.add(line.strip())
        
        return {
            "tool": "chaos",
            "status": "success",
            "data": list(subdomains)
        }
    except Exception as e:
        return {
            "tool": "chaos",
            "status": "error",
            "message": str(e)
        }