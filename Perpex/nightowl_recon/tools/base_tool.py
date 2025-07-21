class BaseTool:
    def __init__(self, timeout=300, rate_limit=10, threads=50):
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.threads = threads                # ✅ Add this
        self.version = "unknown"

    async def scan(self, target):
        raise NotImplementedError("Scan method must be implemented by subclasses.")
