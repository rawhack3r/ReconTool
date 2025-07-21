import logging
import json
import os
from datetime import datetime

class ErrorHandler:
    def __init__(self):
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "nightowl_errors.log")
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("NightOwl")
    
    def log_tool_error(self, tool_name, error, target):
        """Log tool-specific error"""
        error_data = {
            "tool": tool_name,
            "error": str(error),
            "target": target,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.error(f"[{tool_name}] {target} - {error}")
        return error_data
    
    def log_critical(self, message, target):
        """Log critical system error"""
        error_data = {
            "message": message,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "type": "system"
        }
        self.logger.critical(f"[SYSTEM] {target} - {message}")
        return error_data
    
    def save_error_report(self, errors, target):
        """Save error report to file"""
        report_dir = "outputs/errors"
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"{target}_errors.json")
        with open(report_path, "w") as f:
            json.dump(errors, f, indent=2)
        return report_path