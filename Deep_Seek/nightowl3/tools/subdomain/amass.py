import subprocess
import json
import os

def run(target, output_dir):
    output_file = os.path.join(output_dir, "amass.json")
    cmd = f"amass enum -d {target} -json {output_file}"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes
        )
        
        if result.returncode != 0:
            return []
        
        # Parse results
        with open(output_file, "r") as f:
            data = [json.loads(line) for line in f]
        
        return [item["name"] for item in data]
    except:
        return []