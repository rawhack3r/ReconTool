import subprocess
import json
import os
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Run Amass for subdomain enumeration"""
    output_file = f"amass_{target}.json"
    results = {"subdomains": []}
    
    try:
        if progress_callback:
            progress_callback("amass", 10, "Starting Amass...")
        
        # Run Amass
        command = f"amass enum -passive -d {target} -json {output_file}"
        subprocess.run(command, shell=True, check=True)
        
        if progress_callback:
            progress_callback("amass", 50, "Processing results...")
        
        # Parse results
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    results["subdomains"].append({
                        "domain": data['name'],
                        "source": "amass",
                        "resolved": data.get('resolved', False)
                    })
        
        return results
    
    except Exception as e:
        ErrorHandler.log_error("amass", str(e), target)
        raise