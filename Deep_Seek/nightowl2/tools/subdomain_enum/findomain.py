import subprocess
from core.error_handler import ErrorHandler

def run_findomain(target):
    """Run Findomain for subdomain enumeration"""
    try:
        output_file = f"findomain_{target}.txt"
        command = f"findomain -t {target} -u {output_file}"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "findomain",
                "status": "error",
                "message": result.stderr
            }
        
        # Read results from file
        with open(output_file, "r") as f:
            subdomains = [line.strip() for line in f]
        
        return {
            "tool": "findomain",
            "status": "success",
            "data": subdomains
        }
    except Exception as e:
        return {
            "tool": "findomain",
            "status": "error",
            "message": str(e)
        }