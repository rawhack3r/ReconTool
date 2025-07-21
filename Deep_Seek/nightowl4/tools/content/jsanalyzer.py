import requests
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_jsanalyzer(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    js_files = []
    for url in state["live_urls"]:
        cmd = f"katana -u {url} -js-crawl -jc -kf js"
        result = utils.run_command(cmd, verbose=verbose)
        if result:
            js_files.extend(result.splitlines())
    
    secrets = []
    for js_file in js_files:
        try:
            response = requests.get(js_file, timeout=5)
            content = response.text
            if "api" in content and "key" in content:
                secrets.append(js_file)
        except:
            continue
    
    with open(f"{output_dir}/content/js_analysis.txt", "w") as f:
        f.write("\n".join(secrets))
    
    return secrets