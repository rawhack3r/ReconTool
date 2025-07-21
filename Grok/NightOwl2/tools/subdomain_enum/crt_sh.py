
import requests
import json

def fetch_crt_sh(domain, output_file):
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)
        subdomains = set(entry["name_value"].strip() for entry in data)
        with open(output_file, "w") as f:
            f.write("\n".join(sorted(subdomains)))
        return subdomains, ""
    except Exception as e:
        return [], str(e)