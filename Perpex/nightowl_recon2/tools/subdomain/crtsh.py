from tools.base_tool import BaseTool
import aiohttp

class CrtShScanner(BaseTool):
    def __init__(self, timeout=300, rate_limit=10, log_fn=None):
        super().__init__(timeout, rate_limit)
        self.name = "crtsh"
        self.log_fn = log_fn

    async def scan(self, target):
        results = []
        url = f"https://crt.sh/?q=%25.{target}&output=json"
        if self.log_fn:
            self.log_fn(f"[crtsh] Querying {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=self.timeout) as resp:
                data = await resp.json()
                for entry in data:
                    name = entry.get("name_value")
                    if name:
                        for d in name.split("\n"):
                            if self.log_fn:
                                self.log_fn(f"[crtsh] {d}")
                            results.append({"domain": d})
        return results
