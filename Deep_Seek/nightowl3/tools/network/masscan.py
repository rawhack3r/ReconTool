import subprocess
import os

def run(urls, output_dir):
    domains = [urlparse(url).netloc for url in urls]
    input_file = os.path.join(output_dir, "domains.txt")
    with open(input_file, "w") as f:
        f.write("\n".join(domains))
    
    output_file = os.path.join(output_dir, "masscan.txt")
    cmd = f"masscan -iL {input_file} -p1-65535 --rate 1000 -oG {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=3600)
        return ["Masscan completed"]
    except:
        return []