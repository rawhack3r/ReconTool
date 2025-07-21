from core.utils import NightOwlUtils

utils = NightOwlUtils()

def run_massdns(target, output_dir, verbose=False):
    wordlist = "config/wordlists/subdomains.txt"
    resolvers = "config/resolvers.txt"
    output_file = f"{output_dir}/subdomains/massdns.txt"
    cmd = f"massdns -r {resolvers} -t A -o S -w {output_file} {wordlist}"
    return utils.run_command(cmd, verbose=verbose, output_file=output_file)