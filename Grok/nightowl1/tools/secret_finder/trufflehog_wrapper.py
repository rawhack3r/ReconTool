import subprocess
import json
from core.error_handler import ErrorHandler
import os
import re

def run_trufflehog(url, output):
    command = f"trufflehog --no-verification {url} --json > {output}"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_trufflehog_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"TruffleHog failed for {url}: {e.stderr.decode()}")
        return []

def parse_trufflehog_output(output_file):
    secrets = []
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    mobile_pattern = r'\+?[1-9]\d{1,14}'
    with open(output_file, 'r') as f:
        for line in f:
            secret = json.loads(line.strip())
            value = secret.get('Raw', '')
            secrets.append({
                'type': secret.get('DetectorName'),
                'value': value,
                'source': secret.get('SourceMetadata')
            })
            if re.match(email_pattern, value):
                with open("output/important/secret/emails.txt", "a") as f:
                    f.write(f"{value} (Source: {secret.get('SourceMetadata')})\n")
            elif re.match(mobile_pattern, value):
                with open("output/important/secret/mobile.txt", "a") as f:
                    f.write(f"{value} (Source: {secret.get('SourceMetadata')})\n")
            else:
                with open("output/important/secret/other.txt", "a") as f:
                    f.write(f"{secret.get('DetectorName')}: {value} (Source: {secret.get('SourceMetadata')})\n")
    return secrets