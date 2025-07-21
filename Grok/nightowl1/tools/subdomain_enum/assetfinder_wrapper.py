import subprocess
from core.error_handler import ErrorHandler
import os

def run_assetfinder(target, output):
    command = f"assetfinder --subs-only {target} > {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_assetfinder_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"Assetfinder failed for {target}: {e.stderr.decode()}")
        return []

def parse_assetfinder_output(output_file):
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