
import subprocess

def run_amass(target, output_file, api_key=""):
    cmd = f"amass enum -d {target} -o {output_file} -v"
    if api_key:
        cmd += f" -config {api_key}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr