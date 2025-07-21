
import subprocess

def run_dnsx(target, output_file):
    cmd = f"dnsx -d {target} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr