import subprocess
import os

def run(target, output_dir):
    output_file = os.path.join(output_dir, "hakrawler.txt")
    cmd = f"echo {target} | hakrawler -depth 3 -scope subs > {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=1200)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []