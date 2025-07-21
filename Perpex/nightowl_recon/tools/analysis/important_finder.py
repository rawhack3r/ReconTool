from tools.base_tool import BaseTool

class ImportantFinder(BaseTool):
    name = "important_finder"
    important = ["/admin", "/login", "/api"]

    async def scan(self, target):
        return [{"important": path, "url": f"http://{target}{path}"} for path in self.important]
