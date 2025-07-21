import requests
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_chaos(target, output_dir, verbose=False):
    try:
        url = f"https://dns.projectdiscovery.io/dns/{target}/subdomains"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        subdomains = [f"{sub}.{target}" for sub in data.get("subdomains", [])]
        
        output_file = f"{output_dir}/subdomains/chaos.txt"
        with open(output_file, "w") as f:
            f.write("\n".join(subdomains))
        
        return subdomains
    except Exception as e:
        if verbose:
            print(f"Chaos error: {str(e)}")
        return []