import requests

def run(target, output_dir):
    try:
        url = f"https://dns.projectdiscovery.io/dns/{target}/subdomains"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        subdomains = [f"{sub}.{target}" for sub in data.get("subdomains", [])]
        
        # Save to file
        with open(f"{output_dir}/chaos.txt", "w") as f:
            f.write("\n".join(subdomains))
        
        return subdomains
    except:
        return []