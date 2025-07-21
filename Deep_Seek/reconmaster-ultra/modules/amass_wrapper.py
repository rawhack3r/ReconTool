"""
Amass Module Wrapper
"""

import subprocess
from core.utils import run_command

def passive_scan(target, output_file):
    """Run Amass in passive mode"""
    cmd = f"amass enum -passive -d {target} -o {output_file}"
    return run_command(cmd)

def active_scan(target, output_file):
    """Run Amass in active mode"""
    cmd = f"amass enum -active -d {target} -o {output_file}"
    return run_command(cmd)