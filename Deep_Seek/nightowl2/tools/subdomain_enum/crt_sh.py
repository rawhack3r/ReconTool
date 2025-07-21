import requests
import re
from core.error_handler import ErrorHandler

def run_crt_sh(target):
    """Query crt.sh for subdomains"""
    try:
        url = f"https://crt.sh/?q=%.{target}&output=json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        subdomains = set()
        for cert in data:
            name = cert.get("name_value", "")
            if name and target in name:
                # Split multi-line entries
                for sub in name.split("\n"):
                    if sub.strip() and target in sub:
                        subdomains.add(sub.strip())
        
        return {
            "tool": "crt_sh",
            "status": "success",
            "data": list(subdomains)
        }
    except Exception as e:
        return {
            "tool": "crt_sh",
            "status": "error",
            "message": str(e)
        }