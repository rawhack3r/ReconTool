from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_wayback(target, output_dir, verbose=False):
    output_file = f"{output_dir}/info/wayback.txt"
    cmd = f"waybackurls {target} > {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)