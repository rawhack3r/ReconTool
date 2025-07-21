
import subprocess

def run_waybackurls(target, output_file):
    cmd = f"waybackurls {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr