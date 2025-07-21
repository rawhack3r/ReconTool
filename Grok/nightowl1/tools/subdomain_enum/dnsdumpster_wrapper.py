
import sys
import time
from dnsdumpster.DNSDumpsterAPI import DNSDumpsterAPI
from nightowl.core.error_handler import ErrorHandler

def fetch_dnsdumpster(target, output_file):
    for attempt in range(3):
        try:
            res = DNSDumpsterAPI({'verbose': True}).search(target)
            results = set()
            for entry in res.get('dns_records', {}).get('host', []):
                results.add(entry['domain'])
            for entry in res.get('dns_records', {}).get('mx', []):
                results.add(entry['domain'])
            with open(output_file, 'w') as f:
                for result in results:
                    f.write(f"{result}\n")
            ErrorHandler.log_info(f"Successfully fetched {len(results)} records from DNSDumpster for {target}")
            return results
        except Exception as e:
            ErrorHandler.log_error(f"Error fetching DNSDumpster data (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
            continue
    return set()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 dnsdumpster_wrapper.py <target> <output_file>")
        sys.exit(1)
    fetch_dnsdumpster(sys.argv[1], sys.argv[2])