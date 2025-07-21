import os
import json
from datetime import datetime

class ErrorHandler:
    def __init__(self):
        self.errors = []
        self.log_file = "nightowl_errors.log"
    
    def log_error(self, tool, error, target):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "target": target,
            "error": error
        }
        self.errors.append(entry)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def log_critical(self, error, target):
        self.log_error("SYSTEM", error, target)
    
    def get_errors(self):
        return self.errors
    
    def clear_errors(self):
        self.errors = []
        open(self.log_file, "w").close()