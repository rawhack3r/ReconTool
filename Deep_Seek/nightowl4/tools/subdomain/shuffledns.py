from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_shuffledns(target, output_dir, verbose=False):
    wordlist = "config/wordlists/subdomains.txt"
    output_file = f"{output_dir}/subdomains/shuffledns.txt"
    cmd = f"shuffledns -d {target} -w {wordlist} -o {output_file}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)