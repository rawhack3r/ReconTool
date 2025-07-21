import subprocess
import csv
import os
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Run Sublist3r for subdomain enumeration"""
    output_file = f"sublist3r_{target}.csv"
    results = {"subdomains": []}
    
    try:
        if progress_callback:
            progress_callback("sublist3r", 10, "Starting Sublist3r...")
        
        # Run Sublist3r
        command = f"sublist3r -d {target} -o {output_file}"
        subprocess.run(command, shell=True, check=True)
        
        if progress_callback:
            progress_callback("sublist3r", 70, "Processing results...")
        
        # Parse results
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:  # Skip empty rows
                        results["subdomains"].append({
                            "domain": row[0],
                            "source": "sublist3r",
                            "resolved": False
                        })
        
        return results
    
    except Exception as e:
        ErrorHandler.log_error("sublist3r", str(e), target)
        raise