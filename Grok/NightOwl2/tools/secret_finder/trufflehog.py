
import subprocess

def run_trufflehog(target, output_file):
    cmd = f"trufflehog --regex --entropy=True {target} > {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr