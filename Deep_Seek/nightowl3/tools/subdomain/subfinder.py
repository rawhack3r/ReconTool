import subprocess
import json
import os

def run(target, output_dir):
    output_file = os.path.join(output_dir, "subfinder.txt")
    cmd = f"subfinder -d {target} -o {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=1200)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []