from tools.base_tool import BaseTool
import asyncio
import json

class AmassScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10):
        super().__init__(timeout, rate_limit)
        self.name = "amass"

    async def scan(self, target):
        results = []
        cmd = ["amass", "enum", "-d", target, "-json", "-"]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        async for l in proc.stdout:
            try:
                d = json.loads(l)
                results.append({"domain": d.get("name")})
            except Exception:
                pass
        await proc.wait()
        return results
