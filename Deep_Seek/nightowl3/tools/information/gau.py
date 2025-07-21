import subprocess
import os

def run(target, output_dir):
    output_file = os.path.join(output_dir, "gau.txt")
    cmd = f"gau {target} > {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=600)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []