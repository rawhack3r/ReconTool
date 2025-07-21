import subprocess
import os

def run(urls, output_dir):
    wordlist = "config/wordlists/directories.txt"
    output_file = os.path.join(output_dir, "ffuf.txt")
    
    results = []
    for url in urls:
        try:
            cmd = f"ffuf -w {wordlist} -u {url}/FUZZ -o {output_file} -of json"
            subprocess.run(cmd, shell=True, timeout=600)
            
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    data = json.load(f)
                    for result in data.get("results", []):
                        results.append(f"{url}{result['url']}")
        except:
            continue
    
    return results