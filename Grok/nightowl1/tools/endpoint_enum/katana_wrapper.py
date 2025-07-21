import subprocess
from core.error_handler import ErrorHandler
import os

def run_katana(url, output):
    command = f"katana -u {url} -o {output} -js-crawl -hl -depth 5"
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return parse_katana_output(output)
    except subprocess.CalledProcessError as e:
        ErrorHandler.log_error(f"Katana failed for {url}: {e.stderr.decode()}")
        return []

def parse_katana_output(output_file):
    endpoints = []
    with open(output_file, 'r') as f:
        for line in f:
            endpoint = line.strip()
            if endpoint:
                endpoints.append({'endpoint': endpoint})
                with open("output/important/endpoints.txt", "a") as f:
                    f.write(f"{endpoint}\n")
    return endpoints