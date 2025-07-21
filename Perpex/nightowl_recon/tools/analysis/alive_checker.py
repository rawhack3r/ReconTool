from tools.base_tool import BaseTool
import aiohttp

class AliveChecker(BaseTool):
    name = "alive_checker"

    async def scan(self, target):
        results = []
        async with aiohttp.ClientSession() as session:
            for proto in ["http", "https"]:
                url = f"{proto}://{target}"
                try:
                    async with session.get(url, timeout=5) as resp:
                        results.append({"domain": target, "protocol": proto, "status": "alive", "status_code": resp.status})
                except Exception:
                    continue
        return results
