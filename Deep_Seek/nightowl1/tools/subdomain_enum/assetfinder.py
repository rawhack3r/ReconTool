import subprocess
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Run Assetfinder for subdomain enumeration"""
    results = {"subdomains": []}
    
    try:
        if progress_callback:
            progress_callback("assetfinder", 10, "Starting Assetfinder...")
        
        # Run Assetfinder
        command = f"assetfinder --subs-only {target}"
        process = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        if progress_callback:
            progress_callback("assetfinder", 70, "Processing results...")
        
        # Process output
        domains = process.stdout.splitlines()
        for domain in domains:
            if domain.strip():
                results["subdomains"].append({
                    "domain": domain.strip(),
                    "source": "assetfinder",
                    "resolved": False
                })
        
        return results
    
    except Exception as e:
        ErrorHandler.log_error("assetfinder", str(e), target)
        raise