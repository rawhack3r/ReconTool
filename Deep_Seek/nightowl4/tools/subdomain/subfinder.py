from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_subfinder(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/subfinder.txt"
    cmd = f"subfinder -d {target} -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)