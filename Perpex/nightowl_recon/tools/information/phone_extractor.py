from tools.base_tool import BaseTool
import aiohttp, re

class PhoneExtractor(BaseTool):
    name = "phone_extractor"
    PHONE_PATTERN = re.compile(r"\+?\d[\d\s\-.]{8,}\d")

    async def scan(self, target):
        results = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://{target}") as resp:
                    content = await resp.text()
                    for phone in set(self.PHONE_PATTERN.findall(content)):
                        results.append({"phone": phone})
            except Exception:
                pass
        return results
