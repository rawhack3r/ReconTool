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
        self.task_queue = asyncio.Queue()
        self.worker_tasks = []
        
    async def start_workers(self):
        """Start worker tasks for adaptive execution"""
        for _ in range(self.max_threads):
            task = asyncio.create_task(self._worker())
            self.worker_tasks.append(task)
    
    async def stop_workers(self):
        """Stop all worker tasks"""
        for _ in range(self.max_threads):
            await self.task_queue.put(None)
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
    
    async def execute_tool(self, tool_func, *args):
        """Execute tool with adaptive resource management"""
        current_load = self.system_load()
        task_id = id(tool_func)
        
        # Put task in queue
        await self.task_queue.put((tool_func, args, task_id))
        
        # Wait for completion
        while True:
            await asyncio.sleep(0.1)
            if task_id in self.completed_tasks:
                result = self.completed_tasks.pop(task_id)
                if isinstance(result, Exception):
                    raise result
                return result
    
    async def _worker(self):
        """Worker task that processes tool executions"""
        self.completed_tasks = {}
        while True:
            item = await self.task_queue.get()
            if item is None:
                break
                
            tool_func, args, task_id = item
            current_load = self.system_load()
            
            try:
                if current_load['cpu'] > self.cpu_threshold:
                    # Use threading for I/O bound tasks
                    with ThreadPoolExecutor(max_workers=self.dynamic_thread_count()) as executor:
                        loop = asyncio.get_running_loop()
                        result = await loop.run_in_executor(executor, tool_func, *args)
                elif current_load['mem'] > self.mem_threshold:
                    # Use process pool for CPU-bound tasks
                    with ProcessPoolExecutor(max_workers=self.dynamic_process_count()) as executor:
                        loop = asyncio.get_running_loop()
                        result = await loop.run_in_executor(executor, tool_func, *args)
                else:
                    # Direct execution for normal conditions
                    result = tool_func(*args)
                    
                self.completed_tasks[task_id] = result
            except Exception as e:
                self.completed_tasks[task_id] = e
            finally:
                self.task_queue.task_done()
    
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
    def __init__(self, max_size=1000, default_ttl=300):
        self.cache = {}
        self.cache_expiry = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def cache_result(self, key, value, ttl=None):
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        ttl = ttl or self.default_ttl
        self.cache[key] = value
        self.cache_expiry[key] = time.time() + ttl
    
    def get_cached(self, key):
        if key in self.cache:
            if self.cache_expiry.get(key, 0) > time.time():
                self.hits += 1
                return self.cache[key]
            else:
                del self.cache[key]
                del self.cache_expiry[key]
        self.misses += 1
        return None
    
    def _evict_oldest(self):
        if not self.cache_expiry:
            return
            
        oldest_key = min(self.cache_expiry, key=self.cache_expiry.get)
        del self.cache[oldest_key]
        del self.cache_expiry[oldest_key]
    
    def clear_cache(self):
        self.cache.clear()
        self.cache_expiry.clear()
        self.hits = 0
        self.misses = 0
    
    def cache_stats(self):
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / (self.hits + self.misses) if self.hits + self.misses > 0 else 0
        }