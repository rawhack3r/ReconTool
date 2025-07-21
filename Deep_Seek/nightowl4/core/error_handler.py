import logging
from datetime import datetime

class ErrorHandler:
    def __init__(self, log_file="error.log"):
        self.log_file = log_file
        logging.basicConfig(
            filename=log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def log_error(self, tool, error, target):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Tool: {tool}, Target: {target}, Error: {error}\n"
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to log error: {str(e)}")
        
        logging.error(f"{tool} on {target}: {error}")