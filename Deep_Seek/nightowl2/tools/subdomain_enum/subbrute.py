import subprocess
import re
from core.error_handler import ErrorHandler

def run_subbrute(target):
    """Run SubBrute for subdomain enumeration"""
    try:
        command = f"subbrute {target}"
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "subbrute",
                "status": "error",
                "message": result.stderr
            }
        
        # Parse results
        subdomains = []
        for line in result.stdout.splitlines():
            if target in line:
                match = re.search(rf"([\w\-\.]+\.{target})", line)
                if match:
                    subdomains.append(match.group(1))
        
        return {
            "tool": "subbrute",
            "status": "success",
            "data": list(set(subdomains))
        }
    except Exception as e:
        return {
            "tool": "subbrute",
            "status": "error",
            "message": str(e)
        }