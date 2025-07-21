
import requests
import json

def fetch_hunter_io(domain, api_key, output_file):
    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)
        emails = [email["value"] for email in data.get("data", {}).get("emails", [])]
        with open(output_file, "w") as f:
            f.write("\n".join(emails))
        return emails, ""
    except Exception as e:
        return [], str(e)