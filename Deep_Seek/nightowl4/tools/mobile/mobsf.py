import json
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_mobile_analysis(target, output_dir, state, verbose=False):
    if not (target.endswith(".apk") or target.endswith(".ipa")):
        return {}
    
    output_file = f"{output_dir}/mobile/mobsf.json"
    cmd = f"mobsfscan {target} --json -o {output_file}"
    result = utils.run_command(cmd, verbose=verbose)
    if result and os.path.exists(output_file):
        with open(output_file, "r") as f:
            return json.load(f)
    return {}