import subprocess
from core.error_handler import ErrorHandler
import os

def run_sublist3r(target, output):
    command = f"sublist3r -d {target} -o {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_sublist3r_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"Sublist3r failed for {target}: {e.stderr.decode()}")
        return []

def parse_sublist3r_output(output_file):
    subdomains = []
    with open(output_file, 'r') as f:
        for line in f:
            subdomain = line.strip()
            if subdomain:
                subdomains.append({'subdomain': subdomain, 'resolved': False})
    with open("output/subdomains.txt", "a") as f:
        for subdomain in subdomains:
            f.write(f"{subdomain['subdomain']}\n")
    with open("output/non_resolved.txt", "a") as f:
        for subdomain in subdomains:
            if not subdomain['resolved']:
                f.write(f"{subdomain['subdomain']}\n")
    return subdomains