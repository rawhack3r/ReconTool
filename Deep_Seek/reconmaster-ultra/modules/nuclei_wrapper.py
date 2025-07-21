"""
Nuclei Module Wrapper
"""

from core.utils import run_command

def run(input_file, output_file, templates):
    """Run Nuclei with specified templates"""
    cmd = f"nuclei -l {input_file} -t {templates} -json -o {output_file}"
    return run_command(cmd)