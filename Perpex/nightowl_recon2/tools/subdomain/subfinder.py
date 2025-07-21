from tools.base_tool import BaseTool
import asyncio
import json

class SubfinderScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10, log_fn=None):
        super().__init__(timeout, rate_limit)
        self.name = "subfinder"
        self.log_fn = log_fn

    async def scan(self, target):
        results = []
        cmd = ["subfinder", "-d", target, "-all", "-silent", "-json"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        async for line in proc.stdout:
            line = line.decode().strip()
            if not line:
                continue
            try:
                js = json.loads(line)
                if "host" in js:
                    msg = f"[subfinder] {js['host']}"
                    if self.log_fn:
                        self.log_fn(msg)
                    results.append({"domain": js["host"]})
            except Exception:
                continue
        await proc.wait()
        return results
