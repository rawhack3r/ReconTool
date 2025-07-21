import sys
import requests
from bs4 import BeautifulSoup
import time

def get_dnsdumpster_subdomains(domain):
    try:
        url = "https://dnsdumpster.com/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://dnsdumpster.com/"
        }
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
        data = {
            "csrfmiddlewaretoken": csrf_token,
            "targetip": domain,
            "user": "free"
        }
        time.sleep(1)  # Avoid rate limiting
        response = session.post(url, headers=headers, data=data, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        subdomains = set()
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) > 0:
                    subdomain = cells[0].text.strip().split("\n")[0]
                    if subdomain.endswith(domain):
                        subdomains.add(subdomain)
        return subdomains
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return set()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 dnsdumpster.py <domain>", file=sys.stderr)
        sys.exit(1)
    domain = sys.argv[1]
    subdomains = get_dnsdumpster_subdomains(domain)
    for subdomain in sorted(subdomains):
        print(subdomain)