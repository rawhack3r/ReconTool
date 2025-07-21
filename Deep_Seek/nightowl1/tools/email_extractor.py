import re
from core.error_handler import ErrorHandler

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def extract_emails(content, target_domain):
    """Extract emails from text content"""
    emails = set()
    try:
        matches = re.finditer(EMAIL_REGEX, content, re.MULTILINE)
        for match in matches:
            email = match.group().lower()
            if email.endswith(f"@{target_domain}") or f".{target_domain}" in email:
                emails.add(email)
    except Exception as e:
        ErrorHandler.log_error("email_extractor", str(e), target_domain)
    
    return list(emails)