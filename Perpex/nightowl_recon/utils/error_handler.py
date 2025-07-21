import logging
from pathlib import Path

class ErrorHandler:
    def __init__(self, output_dir):
        self.err_log = Path(output_dir) / "logs/errors.log"
        self.err_log.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=str(self.err_log), level=logging.WARNING)

    def log_error(self, tool_name, message, target):
        msg = f"{tool_name} on {target} => {message}"
        logging.error(msg)

    def flush(self):
        logging.shutdown()
