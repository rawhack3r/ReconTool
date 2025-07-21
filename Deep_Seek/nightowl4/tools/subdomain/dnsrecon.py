import json
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_dnsrecon(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/dnsrecon.txt"
    cmd = f"dnsrecon -d {target} -t std -j {output_file}"
    result = utils.run_command(cmd, verbose=verbose)
    if result:
        try:
            with open(output_file, "r") as f:
                data = json.load(f)
            return [record["name"] for record in data if "name" in record]
        except:
            return []
    return []