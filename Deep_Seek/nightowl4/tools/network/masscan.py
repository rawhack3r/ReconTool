from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_masscan(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    output_file = f"{output_dir}/network/masscan.txt"
    cmd = f"masscan -p1-65535 -iL {output_dir}/live_hosts/urls.txt -oG {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)