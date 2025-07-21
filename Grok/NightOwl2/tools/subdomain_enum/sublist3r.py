
import subprocess

def run_sublist3r(target, output_file):
    cmd = f"sublist3r -d {target} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr