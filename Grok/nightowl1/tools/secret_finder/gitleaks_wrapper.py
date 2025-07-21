import subprocess
import json
from core.error_handler import ErrorHandler
import os
import re

def run_gitleaks(url, output):
    command = f"gitleaks detect --source {url} --report-format json --report-path {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_gitleaks_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"Gitleaks failed for {url}: {e.stderr.decode()}")
        return []

def parse_gitleaks_output(output_file):
    secrets = []
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    mobile_pattern = r'\+?[1-9]\d{1,14}'
    with open(output_file, 'r') as f:
        data = json.load(f)
        for secret in data:
            value = secret.get('Secret', '')
            secrets.append({
                'type': secret.get('Description'),
                'value': value,
                'source': secret.get('File')
            })
            if re.match(email_pattern, value):
                with open("output/important/secret/emails.txt", "a") as f:
                    f.write(f"{value} (Source: {secret.get('File')})\n")
            elif re.match(mobile_pattern, value):
                with open("output/important/secret/mobile.txt", "a") as f:
                    f.write(f"{value} (Source: {secret.get('File')})\n")
            else:
                with open("output/important/secret/other.txt", "a") as f:
                    f.write(f"{secret.get('Description')}: {value} (Source: {secret.get('File')})\n")
    return secrets