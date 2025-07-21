from tools.base_tool import BaseTool
import aiohttp, re

class NameExtractor(BaseTool):
    name = "name_extractor"
    # This is a placeholder implementation. Use better NLP for real use.
    NAME_PATTERN = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")

    async def scan(self, target):
        results = []
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"http://{target}") as resp:
                    content = await resp.text()
                    for name in set(self.NAME_PATTERN.findall(content)):
                        results.append({"name": name})
            except Exception:
                pass
        return results
