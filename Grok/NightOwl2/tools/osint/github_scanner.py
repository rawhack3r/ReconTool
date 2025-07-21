
import requests
import re

def scan_github(target, output_file):
    try:
        query = f"from:{target}"
        url = f"https://api.github.com/search/code?q={query}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = json.loads(response.text)
        secrets = []
        for item in data.get("items", []):
            content = requests.get(item["url"], headers=headers, timeout=10).text
            secrets.extend(re.findall(r"(?i)(api_key|password|token)=[A-Za-z0-9]{16,64}", content))
        with open(output_file, "w") as f:
            f.write("\n".join(secrets))
        return secrets, ""
    except Exception as e:
        return [], str(e)