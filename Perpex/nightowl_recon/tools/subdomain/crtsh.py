# tools/subdomain/crtsh.py

from tools.base_tool import BaseTool
import aiohttp
import asyncio

class CrtShScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10):
        super().__init__(timeout, rate_limit)
        self.name = "crtsh"

    async def scan(self, target):
        results = []
        url = f"https://crt.sh/?q=%25.{target}&output=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=self.timeout) as resp:
                data = await resp.json()
                for entry in data:
                    name = entry.get("name_value")
                    if name:
                        for d in name.split("\n"):
                            results.append({"domain": d})
        return results
