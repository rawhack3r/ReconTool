class BaseTool:
    def __init__(self, timeout=300, rate_limit=10):
        self.timeout = timeout
        self.rate_limit = rate_limit
    async def scan(self, target):
        raise NotImplementedError
