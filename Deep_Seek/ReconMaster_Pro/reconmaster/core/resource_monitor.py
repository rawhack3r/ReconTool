import time
import psutil
from functools import wraps

class ResourceMonitor:
    @staticmethod
    def track(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Initialize metrics
            start_time = time.time()
            cpu_percent = psutil.cpu_percent(interval=None)
            mem_usage = psutil.virtual_memory().used
            
            result = await func(*args, **kwargs)
            
            # Calculate deltas
            return result, {
                "time": time.time() - start_time,
                "cpu": max(0, psutil.cpu_percent(interval=None) - cpu_percent),
                "memory": max(0, (psutil.virtual_memory().used - mem_usage) / (1024 ** 2))
            }
        return wrapper