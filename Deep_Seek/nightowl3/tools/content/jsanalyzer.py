import subprocess
import os
import re

def run(urls, output_dir):
    js_files = []
    for url in urls:
        try:
            cmd = f"katana -u {url} -js-crawl -jc -kf js"
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                js_files.extend(result.stdout.splitlines())
        except:
            continue
    
    # Analyze JS files for secrets
    secrets = []
    for js_file in js_files:
        try:
            response = requests.get(js_file, timeout=5)
            content = response.text
            # Look for API keys, tokens, etc.
            if "api" in content and "key" in content:
                secrets.append(js_file)
        except:
            continue
    
    # Save to file
    with open(f"{output_dir}/js_analysis.txt", "w") as f:
        f.write("\n".join(secrets))
    
    return secrets