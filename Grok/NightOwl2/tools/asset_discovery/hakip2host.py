
import subprocess

def run_hakip2host(target, output_file):
    cmd = f"hakip2host {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr
