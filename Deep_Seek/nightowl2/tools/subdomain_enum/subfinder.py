import subprocess
import json
from core.error_handler import ErrorHandler

def run_subfinder(target):
    """Run Subfinder for subdomain enumeration"""
    try:
        output_file = f"subfinder_{target}.json"
        command = f"subfinder -d {target} -oJ -o {output_file}"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "subfinder",
                "status": "error",
                "message": result.stderr
            }
        
        # Parse JSON results
        with open(output_file, "r") as f:
            results = [json.loads(line) for line in f]
        
        subdomains = [r['host'] for r in results]
        return {
            "tool": "subfinder",
            "status": "success",
            "data": subdomains
        }
    except Exception as e:
        return {
            "tool": "subfinder",
            "status": "error",
            "message": str(e)
        }