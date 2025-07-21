from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_sublist3r(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/sublist3r.txt"
    cmd = f"sublist3r -d {target} -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)