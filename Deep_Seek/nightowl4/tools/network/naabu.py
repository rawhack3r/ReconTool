from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_naabu(target, output_dir, state, verbose=False):
    if not state.get("live_urls"):
        return []
    
    output_file = f"{output_dir}/network/naabu.txt"
    cmd = f"naabu -list {output_dir}/live_hosts/urls.txt -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)