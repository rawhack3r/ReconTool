
import subprocess

def run_whois(target, output_file):
    cmd = f"whois {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr