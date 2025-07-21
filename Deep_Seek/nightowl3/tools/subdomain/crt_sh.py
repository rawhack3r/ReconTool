import requests

def run(target, output_dir):
    try:
        url = f"https://crt.sh/?q=%.{target}&output=json"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        subdomains = set()
        for cert in data:
            name = cert.get("name_value", "")
            if name and target in name:
                # Split multi-line entries
                for sub in name.split("\n"):
                    if sub.strip() and target in sub:
                        subdomains.add(sub.strip())
        
        # Save to file
        with open(f"{output_dir}/crt_sh.txt", "w") as f:
            f.write("\n".join(subdomains))
        
        return list(subdomains)
    except:
        return []