import time
import psutil
from core.error_handler import ErrorHandler, ErrorType, ErrorLevel

class ResilienceManager:
    def __init__(self, config):
        self.config = config
        self.error_handler = ErrorHandler()
        self.checkpoint_interval = config.get('CHECKPOINT_INTERVAL', 300)  # 5 minutes
        self.last_checkpoint = time.time()
        self.max_memory_usage = config.get('MAX_MEMORY', 0.8)  # 80% of RAM
        self.max_cpu_usage = config.get('MAX_CPU', 0.8)  # 80% of CPU
    
    def enforce_limits(self):
        """Enforce resource usage limits"""
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1) / 100
        
        if mem.percent / 100 > self.max_memory_usage:
            self.error_handler.handle(
                "ResilienceManager",
                f"Memory limit exceeded: {mem.percent}% > {self.max_memory_usage*100}%",
                "ResourceMonitoring",
                ErrorLevel.CRITICAL,
                ErrorType.RESOURCE
            )
            return False
        
        if cpu > self.max_cpu_usage:
            self.error_handler.handle(
                "ResilienceManager",
                f"CPU limit exceeded: {cpu*100}% > {self.max_cpu_usage*100}%",
                "ResourceMonitoring",
                ErrorLevel.CRITICAL,
                ErrorType.RESOURCE
            )
            return False
        
        return True
    
    def should_checkpoint(self):
        """Determine if it's time for a checkpoint"""
        current_time = time.time()
        if current_time - self.last_checkpoint >= self.checkpoint_interval:
            self.last_checkpoint = current_time
            return True
        return False
    
    def graceful_degradation(self, state):
        """Implement graceful degradation under load"""
        if not self.enforce_limits():
            # Reduce workload by 50%
            state['config']['MAX_WORKERS'] = max(1, state['config']['MAX_WORKERS'] // 2)
            state['config']['SCAN_INTENSITY'] = "medium"
            logging.warning("Entering degraded mode - reduced workload")
        
        return state
    
    def handle_crash(self, exception, state):
        """Handle application crashes"""
        error_id = self.error_handler.handle(
            "ResilienceManager",
            f"Application crash: {str(exception)}",
            "CrashRecovery",
            ErrorLevel.CRITICAL,
            ErrorType.UNKNOWN,
            recoverable=False
        )['id']
        
        # Attempt to save state
        from core.state_manager import StateManager
        StateManager.save_state(state['target'], state)
        
        logging.critical(f"Crash handled. State saved. Error ID: {error_id}")
        return error_id