
import subprocess

def run_puredns(target, output_file, wordlist="data/wordlists/subdomains.txt"):
    cmd = f"puredns bruteforce {target} -w {wordlist} -o {output_file} --resolvers data/wordlists/resolvers.txt"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr