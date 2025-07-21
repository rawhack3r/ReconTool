
import subprocess

def run_katana(target, output_file):
    cmd = f"katana -u {target} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr