
import requests
import time
from nightowl.core.error_handler import ErrorHandler

def fetch_subdomains(target, output_file):
    for attempt in range(3):
        try:
            url = f"https://crt.sh/?q=%.{target}&output=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            subdomains = {entry['name_value'] for entry in response.json()}
            with open(output_file, 'w') as f:
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
            ErrorHandler.log_info(f"Successfully fetched {len(subdomains)} subdomains from crt.sh for {target}")
            return subdomains
        except Exception as e:
            ErrorHandler.log_error(f"Error fetching subdomains from crt.sh (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            continue
    return set()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python3 crt_sh_wrapper.py <target> <output_file>")
        sys.exit(1)
    fetch_subdomains(sys.argv[1], sys.argv[2])