
import subprocess

def run_ffuf(target, output_file, wordlist="data/wordlists/directories.txt"):
    cmd = f"ffuf -u {target}/FUZZ -w {wordlist} -o {output_file} -v"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr