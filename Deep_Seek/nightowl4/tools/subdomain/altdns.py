from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_altdns(target, output_dir, verbose=False):
    input_file = f"{output_dir}/subdomains/all.txt"
    output_file = f"{output_dir}/subdomains/altdns.txt"
    cmd = f"altdns -i {input_file} -o {output_file} -w config/wordlists/altdns_words.txt"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)