
import subprocess

def run_cloud_scanner(target, output_file):
    cmd = f"S3Scanner scan {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr
