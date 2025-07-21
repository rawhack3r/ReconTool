import subprocess
import os

def run(target, output_dir):
    wordlist = "config/wordlists/subdomains.txt"
    output_file = os.path.join(output_dir, "shuffledns.txt")
    cmd = f"shuffledns -d {target} -w {wordlist} -o {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=1800)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []