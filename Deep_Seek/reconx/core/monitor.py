import psutil
import time

class ResourceMonitor:
    def __init__(self):
        self.active_tasks = {}
        self.max_cpu_usage = 0
        self.max_ram_usage = 0
        self.start_time = time.time()
        
    def start_task(self, task_name):
        self.active_tasks[task_name] = {
            'start_time': time.time(),
            'initial_cpu': psutil.cpu_percent(),
            'initial_ram': psutil.virtual_memory().used
        }
        
    def end_task(self, task_name):
        if task_name not in self.active_tasks:
            return None
            
        task_data = self.active_tasks.pop(task_name)
        end_time = time.time()
        
        # Calculate resource usage
        current_cpu = psutil.cpu_percent()
        current_ram = psutil.virtual_memory().used
        cpu_usage = current_cpu - task_data['initial_cpu']
        ram_usage = (current_ram - task_data['initial_ram']) / (1024 * 1024)  # MB
        
        # Update max usage
        self.max_cpu_usage = max(self.max_cpu_usage, cpu_usage)
        self.max_ram_usage = max(self.max_ram_usage, ram_usage)
        
        return {
            'duration': end_time - task_data['start_time'],
            'cpu': cpu_usage,
            'ram': ram_usage
        }
    
    def get_system_stats(self):
        return {
            'cpu_usage': psutil.cpu_percent(),
            'ram_usage': psutil.virtual_memory().percent,
            'ram_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            'uptime': time.time() - self.start_time
        }
    
    def get_peak_usage(self):
        return {
            'max_cpu': self.max_cpu_usage,
            'max_ram': self.max_ram_usage
        }
    
    def check_resource_limits(self, max_cpu=80, max_ram=80):
        """Check if system resources are within safe limits"""
        stats = self.get_system_stats()
        if stats['cpu_usage'] > max_cpu:
            raise ResourceWarning(f"CPU usage exceeded limit: {stats['cpu_usage']}% > {max_cpu}%")
        if stats['ram_usage'] > max_ram:
            raise ResourceWarning(f"RAM usage exceeded limit: {stats['ram_usage']}% > {max_ram}%")
        return True