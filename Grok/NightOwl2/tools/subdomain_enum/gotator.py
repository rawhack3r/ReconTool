
import subprocess

def run_gotator(target, output_file):
    cmd = f"gotator -d {target} -o {output_file} -silent"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr