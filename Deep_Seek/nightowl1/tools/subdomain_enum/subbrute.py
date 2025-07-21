import subprocess
import os
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Run SubBrute for subdomain enumeration"""
    output_file = f"subbrute_{target}.txt"
    results = {"subdomains": []}
    
    try:
        if progress_callback:
            progress_callback("subbrute", 10, "Starting SubBrute...")
        
        # Run SubBrute
        command = f"python3 subbrute.py {target} > {output_file}"
        subprocess.run(command, shell=True, check=True)
        
        if progress_callback:
            progress_callback("subbrute", 70, "Processing results...")
        
        # Parse results
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for domain in f:
                    results["subdomains"].append({
                        "domain": domain.strip(),
                        "source": "subbrute",
                        "resolved": False
                    })
        
        return results
    
    except Exception as e:
        ErrorHandler.log_error("subbrute", str(e), target)
        raise