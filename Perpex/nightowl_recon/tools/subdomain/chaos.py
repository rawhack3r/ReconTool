from tools.base_tool import BaseTool
import aiohttp

class ChaosScanner(BaseTool):
    name = "chaos"
    async def scan(self, target):
        import os
        api_key = os.getenv('CHAOS_API_KEY')
        if not api_key:
            return []
        url = f"https://dns.projectdiscovery.io/dns/{target}/subdomains"
        headers = {'Authorization': api_key}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [{"domain": name} for name in data.get("subdomains",[])]
        return []
