import psutil
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class AdaptiveExecutor:
    def __init__(self, max_threads=50, max_processes=8):
        self.cpu_threshold = 75
        self.mem_threshold = 85
        self.max_threads = max_threads
        self.max_processes = max_processes
        self.last_adjust = time.time()
        self.cooldown = 30  # seconds between adjustments
    
    async def execute_tool(self, tool_func, *args):
        current_load = self.system_load()
        
        if current_load['cpu'] > self.cpu_threshold:
            # Use threading for I/O bound tasks
            with ThreadPoolExecutor(max_workers=self.dynamic_thread_count()) as executor:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(executor, tool_func, *args)
        elif current_load['mem'] > self.mem_threshold:
            # Use process pool for CPU-bound tasks
            with ProcessPoolExecutor(max_workers=self.dynamic_process_count()) as executor:
                loop = asyncio.get_running_loop()
                return await loop.run_in_executor(executor, tool_func, *args)
        else:
            # Direct execution for normal conditions
            return tool_func(*args)
    
    def system_load(self):
        return {
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent
        }
    
    def dynamic_thread_count(self):
        load = self.system_load()
        if time.time() - self.last_adjust > self.cooldown:
            if load['cpu'] > 90:
                self.max_threads = max(10, self.max_threads - 5)
            elif load['cpu'] < 50:
                self.max_threads = min(50, self.max_threads + 5)
            self.last_adjust = time.time()
        return self.max_threads
    
    def dynamic_process_count(self):
        load = self.system_load()
        if time.time() - self.last_adjust > self.cooldown:
            if load['mem'] > 90:
                self.max_processes = max(2, self.max_processes - 2)
            elif load['mem'] < 60:
                self.max_processes = min(8, self.max_processes + 2)
            self.last_adjust = time.time()
        return self.max_processes

class MemoryOptimizer:
    def __init__(self):
        self.cache = {}
        self.cache_size = 1000
        self.cache_expiry = {}
    
    def cache_result(self, key, value, ttl=300):
        if len(self.cache) >= self.cache_size:
            self.expire_cache()
        self.cache[key] = value
        self.cache_expiry[key] = time.time() + ttl
    
    def get_cached(self, key):
        if key in self.cache and self.cache_expiry.get(key, 0) > time.time():
            return self.cache[key]
        return None
    
    def expire_cache(self):
        current_time = time.time()
        expired_keys = [k for k, exp in self.cache_expiry.items() if exp < current_time]
        for key in expired_keys[:100]:
            del self.cache[key]
            del self.cache_expiry[key]
    
    def clear_cache(self):
        self.cache.clear()
        self.cache_expiry.clear()