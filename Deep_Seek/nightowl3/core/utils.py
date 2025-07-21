import os
import re
import json
import yaml
import requests
import socket
import subprocess
from urllib.parse import urlparse

class Utils:
    @staticmethod
    def load_patterns(file="config/patterns.yaml"):
        with open(file, "r") as f:
            return yaml.safe_load(f)
    
    @staticmethod
    def check_alive(domains, output_dir=None):
        alive = []
        for domain in domains:
            try:
                socket.create_connection((domain, 80), timeout=1)
                alive.append(domain)
            except:
                continue
        
        if output_dir:
            with open(f"{output_dir}/alive.txt", "w") as f:
                f.write("\n".join(alive))
        
        return alive
    
    @staticmethod
    def get_important_domains(domains, output_dir=None):
        patterns = ["admin", "staging", "dev", "test", "internal", "secure", "vpn", "api"]
        important = [d for d in domains if any(p in d for p in patterns)]
        
        if output_dir:
            with open(f"{output_dir}/important.txt", "w") as f:
                f.write("\n".join(important))
        
        return important
    
    @staticmethod
    def extract_emails(content):
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(pattern, content)))
    
    @staticmethod
    def extract_phones(content):
        pattern = r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        return list(set(re.findall(pattern, content)))
    
    @staticmethod
    def extract_names(content):
        pattern = r'\b(?:Mr\.|Mrs\.|Ms\.|Dr\.)?\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        return list(set(re.findall(pattern, content)))
    
    @staticmethod
    def extract_secrets(content):
        secrets = []
        patterns = Utils.load_patterns().get("secrets", {})
        for name, pattern in patterns.items():
            secrets.extend(re.findall(pattern, content))
        return secrets
    
    @staticmethod
    def get_juicy_files(urls):
        juicy = []
        patterns = [r'\.(bak|old|sql|backup|conf|config|env|swp)\b', r'(admin|backup|config|secret)']
        for url in urls:
            if any(re.search(p, url) for p in patterns):
                juicy.append(url)
        return juicy
    
    @staticmethod
    def find_buckets(domains):
        buckets = []
        for domain in domains:
            # Check common bucket URLs
            for provider in ["s3", "gs", "az"]:
                bucket_url = f"{provider}://{domain}"
                try:
                    response = requests.head(bucket_url, timeout=2)
                    if response.status_code == 200:
                        buckets.append(bucket_url)
                except:
                    continue
        return buckets
    
    @staticmethod
    def run_command(cmd, timeout=300):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return ""
        except Exception as e:
            return f"Error: {str(e)}"