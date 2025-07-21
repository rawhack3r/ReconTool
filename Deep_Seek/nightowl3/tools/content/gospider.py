import subprocess
import os

def run(urls, output_dir):
    input_file = os.path.join(output_dir, "urls.txt")
    with open(input_file, "w") as f:
        f.write("\n".join(urls))
    
    output_file = os.path.join(output_dir, "gospider.txt")
    cmd = f"gospider -S {input_file} -o {output_file} -t 50"
    
    try:
        subprocess.run(cmd, shell=True, timeout=1800)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []