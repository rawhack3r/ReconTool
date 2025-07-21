import subprocess
import json
from core.error_handler import ErrorHandler
import os

def run_ffuf(url, wordlist, output):
    command = f"ffuf -u {url}/FUZZ -w {wordlist} -o {output} -of json"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_ffuf_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"ffuf failed for {url}: {e.stderr.decode()}")
        return []

def parse_ffuf_output(output_file):
    endpoints = []
    with open(output_file, 'r') as f:
        data = json.load(f)
        for result in data['results']:
            endpoint = result['url']
            endpoints.append({'endpoint': endpoint})
            with open("output/important/endpoints.txt", "a") as f:
                f.write(f"{endpoint}\n")
    return endpoints