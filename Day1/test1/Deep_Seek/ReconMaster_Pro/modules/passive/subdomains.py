import asyncio
from typing import List

async def run_subfinder(target: str, config: dict) -> List[str]:
    """Run subfinder with configurable parameters"""
    threads = config.get("threads", 50)
    cmd = f"subfinder -d {target} -t {threads} -silent"
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        return stdout.decode().splitlines()
    return []

async def run_amass(target: str, config: dict) -> List[str]:
    """Run amass with config file"""
    config_path = config.get("config_path", "configs/amass.ini")
    cmd = f"amass enum -passive -d {target} -config {config_path}"
    
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, _ = await proc.communicate()
    if proc.returncode == 0:
        return stdout.decode().splitlines()
    return []