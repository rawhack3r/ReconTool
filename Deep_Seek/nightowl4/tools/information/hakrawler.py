from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_hakrawler(target, output_dir, verbose=False):
    output_file = f"{output_dir}/info/hakrawler.txt"
    cmd = f"hakrawler -url {target} -depth 2 -plain > {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)