import subprocess
import json
import os
from core.error_handler import ErrorHandler

def run_amass(target):
    """Run Amass for subdomain enumeration"""
    try:
        output_file = f"amass_{target}.json"
        command = f"amass enum -d {target} -json {output_file}"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=1200  # 20 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "amass",
                "status": "error",
                "message": result.stderr
            }
        
        # Parse results
        with open(output_file, "r") as f:
            results = [json.loads(line) for line in f]
        
        subdomains = [r["name"] for r in results]
        ips = [r["addresses"][0]["ip"] for r in results if r.get("addresses")]
        
        return {
            "tool": "amass",
            "status": "success",
            "data": {
                "subdomains": subdomains,
                "ips": ips
            }
        }
    except Exception as e:
        return {
            "tool": "amass",
            "status": "error",
            "message": str(e)
        }