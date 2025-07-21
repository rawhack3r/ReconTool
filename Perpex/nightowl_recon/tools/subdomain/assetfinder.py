from tools.base_tool import BaseTool
import asyncio

class AssetfinderScanner(BaseTool):
    name = "assetfinder"

    async def scan(self, target):
        cmd = ["assetfinder", "--subs-only", target]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        lines = []
        async for line in proc.stdout:
            domain = line.decode().strip()
            if domain: lines.append({"domain": domain})
        await proc.wait()
        return lines
