from tools.base_tool import BaseTool
import aiohttp, re

class SecretFinder(BaseTool):
    name = "secret_finder"
    patterns = [
        re.compile(r'ghp_[0-9a-zA-Z]{36}'),  # github
        re.compile(r'xox[baprs]-[0-9a-zA-Z]{10,48}'), # slack
    ]

    async def scan(self, target):
        results = []
        async with aiohttp.ClientSession() as session:
            for url in [f"http://{target}", f"https://{target}/.env"]:
                try:
                    async with session.get(url, timeout=10) as resp:
                        content = await resp.text()
                        for pat in self.patterns:
                            for m in pat.findall(content):
                                results.append({"secret": m, "url": url})
                except Exception:
                    pass
        return results
