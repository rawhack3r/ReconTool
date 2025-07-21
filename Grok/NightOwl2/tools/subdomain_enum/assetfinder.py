
import subprocess

def run_assetfinder(target, output_file):
    cmd = f"assetfinder --subs-only {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr