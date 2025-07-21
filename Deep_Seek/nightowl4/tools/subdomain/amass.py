from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_amass(target, output_dir, verbose=False):
    output_file = f"{output_dir}/subdomains/amass.txt"
    cmd = f"amass enum -passive -d {target} -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)