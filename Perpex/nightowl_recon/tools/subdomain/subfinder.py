from tools.base_tool import BaseTool
import asyncio, json

class SubfinderScanner(BaseTool):
    name = "subfinder"
    async def scan(self, target):
        cmd = ["subfinder","-d",target,"-json"]
        proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE)
        results = []
        async for line in proc.stdout:
            try: results.append(json.loads(line.decode()))
            except Exception: continue
        await proc.wait()
        return [{"domain": x.get("host")} for x in results]
