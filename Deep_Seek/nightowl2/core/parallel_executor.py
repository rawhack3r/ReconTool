import asyncio
import concurrent.futures
import queue
import psutil
import logging
from enum import Enum
from functools import partial
from core.error_handler import ErrorHandler, ErrorType, ErrorLevel

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParallelExecutor")

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4

class ResourceMonitor:
    def __init__(self):
        self.warning_threshold = 0.7  # 70% resource usage
        self.critical_threshold = 0.9  # 90% resource usage
    
    def check_resources(self):
        """Check system resources and log warnings if thresholds are exceeded"""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        
        if mem.percent / 100 > self.critical_threshold:
            logger.critical(f"Critical memory usage: {mem.percent}%")
            raise ResourceWarning("Critical memory usage - pausing execution")
        if cpu > self.critical_threshold * 100:
            logger.critical(f"Critical CPU usage: {cpu}%")
            raise ResourceWarning("Critical CPU usage - pausing execution")
        
        if mem.percent / 100 > self.warning_threshold:
            logger.warning(f"High memory usage: {mem.percent}%")
        if cpu > self.warning_threshold * 100:
            logger.warning(f"High CPU usage: {cpu}%")

class ParallelExecutor:
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or (psutil.cpu_count() * 2)
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = concurrent.futures.ProcessPoolExecutor(max_workers=max(1, self.max_workers//2))
        self.error_handler = ErrorHandler()
        self.priority_queue = queue.PriorityQueue()
        self.resource_monitor = ResourceMonitor()
        self.active_tasks = 0
        self.max_memory = 0.8  # 80% of available memory
        self.loop = asyncio.get_event_loop()
    
    async def run_tool(self, tool_func, target, phase, priority=Priority.MEDIUM, timeout=300):
        """Run a tool function with priority management and resource monitoring"""
        try:
            self.resource_monitor.check_resources()
            
            # Wrap tool function with safety features
            safe_func = partial(
                self._run_tool_safely, 
                tool_func, 
                target, 
                phase,
                timeout
            )
            
            # Add to priority queue
            self.priority_queue.put((priority.value, safe_func))
            self.active_tasks += 1
            
            # Process queue
            while not self.priority_queue.empty():
                _, task_func = self.priority_queue.get()
                try:
                    return await self.loop.run_in_executor(self.thread_executor, task_func)
                except Exception as e:
                    self.error_handler.handle(
                        tool_func.__name__,
                        str(e),
                        phase,
                        ErrorLevel.ERROR,
                        ErrorType.UNKNOWN
                    )
        except ResourceWarning as rw:
            logger.warning(f"Resource warning: {str(rw)} - Task queued")
            # Requeue the task with higher priority
            return await self.run_tool(tool_func, target, phase, Priority.CRITICAL, timeout)
        finally:
            self.active_tasks -= 1
    
    async def run_cpu_intensive(self, func, *args, priority=Priority.HIGH, timeout=600):
        """Run CPU-intensive tasks in separate processes"""
        try:
            self.resource_monitor.check_resources()
            future = self.process_executor.submit(func, *args)
            return await asyncio.wait_for(self.loop.run_in_executor(None, future.result), timeout)
        except asyncio.TimeoutError:
            self.error_handler.handle(
                func.__name__,
                f"Process timed out after {timeout} seconds",
                "CPU-Intensive",
                ErrorLevel.ERROR,
                ErrorType.TIMEOUT,
                recoverable=True
            )
            return None
        except ResourceWarning as rw:
            logger.warning(f"Resource warning: {str(rw)} - Retrying CPU task")
            # Retry with higher priority
            return await self.run_cpu_intensive(func, *args, Priority.CRITICAL, timeout)
    
    def _run_tool_safely(self, tool_func, target, phase, timeout):
        """Safely execute a tool function with timeout handling"""
        try:
            # Dependency check
            if hasattr(tool_func, 'required_dependencies'):
                dep_check = self.error_handler.check_dependencies(
                    tool_func.__name__,
                    tool_func.required_dependencies
                )
                if dep_check:
                    return dep_check
            
            # Execute with timeout
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(tool_func, target)
                return future.result(timeout=timeout)
                
        except concurrent.futures.TimeoutError:
            self.error_handler.handle(
                tool_func.__name__,
                f"Tool timed out after {timeout} seconds",
                phase,
                ErrorLevel.ERROR,
                ErrorType.TIMEOUT,
                recoverable=True
            )
            return None
        except Exception as e:
            self.error_handler.handle(
                tool_func.__name__,
                str(e),
                phase,
                ErrorLevel.ERROR,
                ErrorType.UNKNOWN,
                recoverable=True
            )
            return None
    
    def shutdown(self):
        """Cleanly shutdown executors"""
        self.thread_executor.shutdown(wait=False)
        self.process_executor.shutdown(wait=False)
        logger.info("Parallel executors shutdown complete")
    
    def get_status(self):
        """Get current executor status"""
        return {
            "active_tasks": self.active_tasks,
            "queued_tasks": self.priority_queue.qsize(),
            "max_workers": self.max_workers,
            "thread_workers": self.thread_executor._max_workers,
            "process_workers": self.process_executor._max_workers
        }