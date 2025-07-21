import subprocess
import csv
from core.error_handler import ErrorHandler

def run_sublister(target):
    """Run Sublist3r for subdomain enumeration"""
    try:
        output_file = f"sublister_{target}.csv"
        command = f"sublist3r -d {target} -o {output_file}"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "sublister",
                "status": "error",
                "message": result.stderr
            }
        
        # Parse CSV results
        subdomains = []
        with open(output_file, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:  # Skip empty rows
                    subdomains.append(row[0])
        
        return {
            "tool": "sublister",
            "status": "success",
            "data": subdomains
        }
    except Exception as e:
        return {
            "tool": "sublister",
            "status": "error",
            "message": str(e)
        }