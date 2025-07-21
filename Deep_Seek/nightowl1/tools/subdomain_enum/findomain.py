import subprocess
import os
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Run Findomain for subdomain enumeration"""
    output_file = f"findomain_{target}.txt"
    results = {"subdomains": []}
    
    try:
        if progress_callback:
            progress_callback("findomain", 10, "Starting Findomain...")
        
        # Run Findomain
        command = f"findomain -t {target} -q -o"
        subprocess.run(command, shell=True, check=True)
        
        if progress_callback:
            progress_callback("findomain", 70, "Processing results...")
        
        # Parse results
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for domain in f:
                    results["subdomains"].append({
                        "domain": domain.strip(),
                        "source": "findomain",
                        "resolved": False
                    })
        
        return results
    
    except Exception as e:
        ErrorHandler.log_error("findomain", str(e), target)
        raise