import subprocess
from core.error_handler import ErrorHandler
import os

def run_gau(target, output):
    command = f"gau {target} > {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_gau_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"gau failed for {target}: {e.stderr.decode()}")
        return []

def parse_gau_output(output_file):
    endpoints = []
    with open(output_file, 'r') as f:
        for line in f:
            endpoint = line.strip()
            if endpoint:
                endpoints.append({'endpoint': endpoint})
                with open("output/important/endpoints.txt", "a") as f:
                    f.write(f"{endpoint}\n")
    return endpoints