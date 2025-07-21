from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_gau(target, output_dir, verbose=False):
    output_file = f"{output_dir}/info/gau.txt"
    cmd = f"gau {target} > {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)