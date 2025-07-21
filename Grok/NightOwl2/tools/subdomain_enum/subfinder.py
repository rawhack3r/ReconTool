
import subprocess

def run_subfinder(target, output_file):
    cmd = f"subfinder -d {target} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr