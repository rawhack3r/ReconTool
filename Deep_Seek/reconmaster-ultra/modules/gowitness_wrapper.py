"""
Gowitness Module Wrapper
"""

from core.utils import run_command

def run(input_file, output_dir):
    """Run Gowitness"""
    cmd = f"gowitness file -s -f {input_file} -d {output_dir}"
    return run_command(cmd)