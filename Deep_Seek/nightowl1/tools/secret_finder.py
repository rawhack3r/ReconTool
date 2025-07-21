import re
import os
import json
from core.error_handler import ErrorHandler

SECRET_PATTERNS = {
    "aws_access_key": r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])",
    "aws_secret_key": r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])",
    "api_key": r"[a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64}",
    "jwt_token": r"eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*",
    "database_url": r"postgres:\/\/[^:]+:[^@]+@[^\/]+\/[^\s]+|mysql:\/\/[^:]+:[^@]+@[^\/]+\/[^\s]+"
}

def run(target, progress_callback=None):
    """Find secrets in source code and files"""
    results = {"secrets": []}
    
    # Get all collected content
    content_files = _get_content_files(target)
    
    for file_path in content_files:
        if progress_callback:
            progress = int(100 * (len(results["secrets"]) + 1) / max(1, len(content_files)))
            progress_callback("secret_finder", progress, f"Scanning {os.path.basename(file_path)}")
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                secrets = _find_secrets(content, file_path)
                results["secrets"].extend(secrets)
        except Exception as e:
            ErrorHandler.log_error("secret_finder", f"Error reading {file_path}: {str(e)}", target)
    
    # Categorize secrets by type
    results["categorized"] = _categorize_secrets(results["secrets"])
    
    return results

def _get_content_files(target):
    """Retrieve all files collected during recon"""
    # In a real implementation, this would scan the output directory
    return [
        f"outputs/scans/content_{target}.json",
        f"outputs/scans/js_{target}.json"
    ]

def _find_secrets(content, source):
    """Find secrets in text content"""
    secrets = []
    
    for secret_type, pattern in SECRET_PATTERNS.items():
        matches = re.finditer(pattern, content)
        for match in matches:
            secret_value = match.group()
            # Avoid false positives with simple checks
            if _is_likely_secret(secret_value, secret_type):
                secrets.append({
                    "type": secret_type,
                    "value": secret_value[:50] + "..." if len(secret_value) > 50 else secret_value,
                    "source": source,
                    "context": content[max(0, match.start()-20):min(len(content), match.end()+20)]
                })
    
    return secrets

def _is_likely_secret(value, secret_type):
    """Simple validation to reduce false positives"""
    if secret_type == "aws_access_key":
        return value.startswith(('AKIA', 'ASIA'))
    return True

def _categorize_secrets(secrets):
    """Categorize secrets by type and criticality"""
    categorized = {}
    for secret in secrets:
        secret_type = secret["type"]
        if secret_type not in categorized:
            categorized[secret_type] = []
        categorized[secret_type].append(secret)
    
    return categorized