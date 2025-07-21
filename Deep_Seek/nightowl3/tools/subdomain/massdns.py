import subprocess
import os

def run(target, output_dir):
    wordlist = "config/wordlists/subdomains.txt"
    output_file = os.path.join(output_dir, "massdns.txt")
    cmd = f"massdns -r config/resolvers.txt -t A -o S -w {output_file} -s 100 {wordlist}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=3600)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return [line.split()[0] for line in f if target in line]
        return []
    except:
        return []