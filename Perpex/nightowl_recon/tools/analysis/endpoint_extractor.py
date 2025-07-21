# tools/analysis/endpoint_extractor.py

import re
from tools.base_tool import BaseTool
import aiohttp

class EndpointExtractor(BaseTool):
    def __init__(self, timeout=300, rate_limit=10, threads=50):
        super().__init__(timeout, rate_limit)
        self.name = "endpoint_extractor"

    async def scan(self, target):
        results = set()
        js_urls = [
            f"https://{target}/",
            f"https://{target}/main.js",
            f"https://{target}/app.js"
        ]

        async with aiohttp.ClientSession() as session:
            for url in js_urls:
                try:
                    async with session.get(url, timeout=self.timeout) as resp:
                        if resp.status == 200:
                            content = await resp.text()
                            endpoints = re.findall(r'["\'](\/(?:api|v\d+\/)[^"\']+?)["\']', content)
                            for ep in endpoints:
                                results.add(ep)
                except Exception as e:
                    continue

        return [{"endpoint": ep} for ep in results]
