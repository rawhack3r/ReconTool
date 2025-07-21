import requests
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_crt_sh(target, output_dir, verbose=False):
    try:
        url = f"https://crt.sh/?q=%.{target}&output=json"
        response = requests.get(url, timeout=30)
        data = response.json()
        
        subdomains = set()
        for cert in data:
            name = cert.get("name_value", "")
            if name and target in name:
                for sub in name.split("\n"):
                    if sub.strip() and target in sub:
                        subdomains.add(sub.strip())
        
        output_file = f"{output_dir}/subdomains/crt_sh.txt"
        with open(output_file, "w") as f:
            f.write("\n".join(subdomains))
        
        return list(subdomains)
    except Exception as e:
        if verbose:
            print(f"crt.sh error: {str(e)}")
        return []