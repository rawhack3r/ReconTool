from tools.base_tool import BaseTool
import asyncio
from pathlib import Path

class DNSXScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10, log_fn=None):
        super().__init__(timeout, rate_limit)
        self.name = "dnsx"
        self.log_fn = log_fn

    async def scan(self, target):
        results = []
        wordlist_path = Path("tools/output/all_subdomains.txt")
        if not wordlist_path.exists():
            if self.log_fn:
                self.log_fn(f"[dnsx] Subdomain input not found: {wordlist_path}")
            return []
        cmd = [
            "dnsx",
            "-silent",
            "-a",
            "-resp",
            "-l", str(wordlist_path)
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
            )
            async for line in proc.stdout:
                line = line.decode().strip()
                if line:
                    if self.log_fn:
                        self.log_fn(f"[dnsx] {line}")
                    results.append({"domain": line})
            await proc.wait()
        except Exception as e:
            if self.log_fn:
                self.log_fn(f"[dnsx] Exception occurred: {e}")
        return results
