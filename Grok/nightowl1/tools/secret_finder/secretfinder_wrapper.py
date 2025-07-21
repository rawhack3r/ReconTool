import subprocess
from core.error_handler import ErrorHandler
import os
import re

def run_secretfinder(url, output):
    command = f"python3 SecretFinder.py -i {url} -o {output} -e"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_secretfinder_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"SecretFinder failed for {url}: {e.stderr.decode()}")
        return []

def parse_secretfinder_output(output_file):
    secrets = []
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    mobile_pattern = r'\+?[1-9]\d{1,14}'
    with open(output_file, 'r') as f:
        for line in f:
            if line.strip():
                value = line.strip()
                secrets.append({'type': 'secret', 'value': value, 'source': output_file})
                if re.match(email_pattern, value):
                    with open("output/important/secret/emails.txt", "a") as f:
                        f.write(f"{value} (Source: {output_file})\n")
                elif re.match(mobile_pattern, value):
                    with open("output/important/secret/mobile.txt", "a") as f:
                        f.write(f"{value} (Source: {output_file})\n")
                else:
                    with open("output/important/secret/other.txt", "a") as f:
                        f.write(f"Secret: {value} (Source: {output_file})\n")
    return secrets