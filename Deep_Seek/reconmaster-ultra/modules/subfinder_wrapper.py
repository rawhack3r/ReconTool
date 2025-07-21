"""
Subfinder Module Wrapper
"""

from core.utils import run_command

def run(target, output_file):
    """Run Subfinder"""
    cmd = f"subfinder -d {target} -o {output_file}"
    return run_command(cmd)