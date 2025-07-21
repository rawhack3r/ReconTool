"""
HTTPX Module Wrapper
"""

from core.utils import run_command

def run(input_file, output_file):
    """Run HTTPX"""
    cmd = f"httpx -l {input_file} -title -status-code -tech-detect -json -o {output_file}"
    return run_command(cmd)