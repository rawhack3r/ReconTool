from tools.base_tool import BaseTool
import asyncio, tempfile, os

class Sublist3rScanner(BaseTool):
    name = "sublist3r"

    async def scan(self, target):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.close()
        cmd = ["python3", "-m", "sublist3r", "-d", target, "-o", tmp.name]
        proc = await asyncio.create_subprocess_exec(*cmd)
        await proc.wait()
        lines = []
        with open(tmp.name) as f:
            for l in f:
                domain = l.strip()
                if domain: lines.append({"domain": domain})
        os.unlink(tmp.name)
        return lines
