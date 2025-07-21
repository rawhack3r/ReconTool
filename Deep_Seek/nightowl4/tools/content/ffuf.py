import json
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_ffuf(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    wordlist = "config/wordlists/directories.txt"
    output_file = f"{output_dir}/content/ffuf.txt"
    results = []
    
    for url in state["live_urls"]:
        cmd = f"ffuf -w {wordlist} -u {url}/FUZZ -o {output_file} -of json"
        result = utils.run_command(cmd, verbose=verbose)
        if result:
            try:
                data = json.loads(result)
                for item in data.get("results", []):
                    results.append(f"{url}{item['url']}")
            except:
                continue
    
    return results