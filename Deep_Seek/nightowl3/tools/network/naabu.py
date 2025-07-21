import subprocess
import os

def run(urls, output_dir):
    domains = [urlparse(url).netloc for url in urls]
    input_file = os.path.join(output_dir, "domains.txt")
    with open(input_file, "w") as f:
        f.write("\n".join(domains))
    
    output_file = os.path.join(output_dir, "naabu.txt")
    cmd = f"naabu -list {input_file} -o {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=1800)
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                return f.read().splitlines()
        return []
    except:
        return []