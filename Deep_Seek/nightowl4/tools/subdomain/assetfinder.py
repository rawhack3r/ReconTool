from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_assetfinder(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/assetfinder.txt"
    cmd = f"assetfinder -subs-only {target} > {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)