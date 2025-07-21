import subprocess
import re
from core.error_handler import ErrorHandler

def run_assetfinder(target):
    """Run Assetfinder for subdomain enumeration"""
    try:
        command = f"assetfinder {target}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "assetfinder",
                "status": "error",
                "message": result.stderr
            }
        
        subdomains = list(set(result.stdout.splitlines()))
        return {
            "tool": "assetfinder",
            "status": "success",
            "data": subdomains
        }
    except Exception as e:
        return {
            "tool": "assetfinder",
            "status": "error",
            "message": str(e)
        }