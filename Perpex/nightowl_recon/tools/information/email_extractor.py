from tools.base_tool import BaseTool
import aiohttp, re

class EmailExtractor(BaseTool):
    name = "email_extractor"

    EMAIL_PATTERN = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', re.I)

    async def scan(self, target):
        results = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://{target}", timeout=10) as resp:
                    content = await resp.text()
                    for email in set(self.EMAIL_PATTERN.findall(content)):
                        results.append({"email": email})
            except Exception:
                pass
        return results
