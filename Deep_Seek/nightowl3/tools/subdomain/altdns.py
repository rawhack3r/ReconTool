import subprocess
import os

def run(target, output_dir):
    input_file = os.path.join(output_dir, "all.txt")
    output_file = os.path.join(output_dir, "altdns.txt")
    
    if not os.path.exists(input_file):
        return []
    
    cmd = f"altdns -i {input_file} -o {output_file} -w config/wordlists/altdns_words.txt"
    
    try:
        subprocess.run(cmd, shell=True, timeout=3600)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []