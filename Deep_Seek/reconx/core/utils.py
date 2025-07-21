import os
import json
import requests
import dns.resolver
from .error_handler import ErrorHandler

def create_directory(path):
    """Safely create directory with error handling"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        ErrorHandler(os.path.dirname(path)).log_error(e, "utils", "directory_creation")
        return False

def run_command(cmd, timeout=300, input_data=None):
    """Execute system command with robust error handling"""
    try:
        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        if result.returncode != 0:
            error_msg = f"Command failed: {' '.join(cmd)}\nError: {result.stderr}"
            raise RuntimeError(error_msg)
        return result.stdout
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timed out: {' '.join(cmd)}")
    except Exception as e:
        raise RuntimeError(f"Command execution error: {str(e)}")

def http_request(url, method='GET', timeout=10):
    """Safe HTTP request with error handling"""
    try:
        response = requests.request(method, url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"HTTP request failed: {str(e)}")

def dns_resolve(domain, record_type='A', resolvers=None):
    """Safe DNS resolution with error handling"""
    try:
        resolver = dns.resolver.Resolver()
        if resolvers:
            resolver.nameservers = resolvers
        return resolver.resolve(domain, record_type)
    except dns.resolver.NXDOMAIN:
        return None
    except Exception as e:
        raise RuntimeError(f"DNS resolution failed: {str(e)}")