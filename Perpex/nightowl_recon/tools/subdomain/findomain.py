# tools/subdomain/findomain.py

from tools.base_tool import BaseTool
import asyncio

class FindomainScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10):
        super().__init__(timeout, rate_limit)
        self.name = "findomain"

    async def scan(self, target):
        results = []
        cmd = ["findomain", "-t", target, "-q", "-oJ"]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        async for line in proc.stdout:
            data = line.decode().strip()
            if data:
                results.append({"domain": data})
        await proc.wait()
        return results
