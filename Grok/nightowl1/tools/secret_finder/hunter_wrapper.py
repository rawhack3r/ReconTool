
import sys
import time
import os
from hunter import Hunter
from nightowl.core.error_handler import ErrorHandler

def fetch_emails(target, output_file):
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key:
        ErrorHandler.log_error("HUNTER_API_KEY not set, skipping Hunter")
        return set()
    for attempt in range(3):
        try:
            hunter = Hunter(api_key)
            results = hunter.domain_search(target)
            emails = {email['value'] for email in results.get('emails', [])}
            with open(output_file, 'w') as f:
                for email in emails:
                    f.write(f"{email}\n")
            ErrorHandler.log_info(f"Successfully fetched {len(emails)} emails from Hunter for {target}")
            return emails
        except Exception as e:
            ErrorHandler.log_error(f"Error fetching emails from Hunter (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            continue
    return set()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 hunter_wrapper.py <target> <output_file>")
        sys.exit(1)
    fetch_emails(sys.argv[1], sys.argv[2])