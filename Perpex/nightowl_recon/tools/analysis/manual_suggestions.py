from tools.base_tool import BaseTool

class ManualSuggestions(BaseTool):
    name = "manual_suggestions"

    async def scan(self, target):
        # In production, pull from config/manual checklist
        return [
            {"suggestion": "Review /important/ for juicy paths and secrets"},
            {"suggestion": "Check /vulnerabilities for critical alerts and verify manually"},
            {"suggestion": "Login as test/test if possible"},
        ]
