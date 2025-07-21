import subprocess
from core.error_handler import ErrorHandler
import os

def run_waybackurls(target, output):
    command = f"waybackurls {target} > {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_waybackurls_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"waybackurls failed for {target}: {e.stderr.decode()}")
        return []

def parse_waybackurls_output(output_file):
    endpoints = []
    with open(output_file, 'r') as f:
        for line in f:
            endpoint = line.strip()
            if endpoint:
                endpoints.append({'endpoint': endpoint})
                with open("output/important/endpoints.txt", "a") as f:
                    f.write(f"{endpoint}\n")
    return endpoints