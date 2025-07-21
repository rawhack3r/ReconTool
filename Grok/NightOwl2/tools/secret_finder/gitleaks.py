
import subprocess

def run_gitleaks(target, output_file):
    cmd = f"gitleaks detect --source {target} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr