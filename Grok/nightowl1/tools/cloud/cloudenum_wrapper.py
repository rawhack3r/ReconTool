import subprocess
from core.error_handler import ErrorHandler
import os

def run_cloudenum(keyword, output):
    command = f"cloud-enum -k {keyword} -o {output} --threads 10"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_cloudenum_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"CloudEnum failed for {keyword}: {e.stderr.decode()}")
        return []

def parse_cloudenum_output(output_file):
    assets = []
    with open(output_file, 'r') as f:
        for line in f:
            asset = line.strip()
            if asset:
                assets.append({'asset': asset})
                with open("output/important/cloud.txt", "a") as f:
                    f.write(f"{asset}\n")
    return assets