
import subprocess

def run_findomain(target, output_file):
    cmd = f"findomain -t {target} -o {output_file} --verbose"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr