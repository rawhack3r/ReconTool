import logging
import os
from datetime import datetime

LOG_DIR = "logs"
ERROR_LOG = os.path.join(LOG_DIR, "nightowl_errors.log")

os.makedirs(LOG_DIR, exist_ok=True)

class ErrorHandler:
    def __init__(self):
        logging.basicConfig(
            filename=ERROR_LOG,
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("NightOwl")
    
    @classmethod
    def capture_error(cls, tool_name, message, target):
        """Capture and log an error"""
        error_data = {
            "tool": tool_name,
            "message": message,
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        cls.log_error(tool_name, message, target)
        return error_data
    
    @classmethod
    def log_error(cls, tool_name, message, target):
        """Log an error to file"""
        logger = logging.getLogger("NightOwl")
        logger.error(f"[{tool_name}] Target: {target} - {message}")
    
    @classmethod
    def log_critical(cls, message, target):
        """Log a critical error"""
        logger = logging.getLogger("NightOwl")
        logger.critical(f"[SYSTEM] Target: {target} - {message}")