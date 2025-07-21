import logging
import traceback
from rich.console import Console

console = Console()

class ErrorHandler:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.log_file = os.path.join(output_dir, "error_log.txt")
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def log_error(self, error, module=None, target=None):
        """Log detailed error information"""
        error_msg = f"{error.__class__.__name__}: {str(error)}"
        if module:
            error_msg = f"[{module}] {error_msg}"
        if target:
            error_msg = f"[{target}] {error_msg}"
            
        # Log to file
        logging.error(error_msg)
        logging.error(traceback.format_exc())
        
        # Print to console
        console.print(f"[red]ERROR: {error_msg}[/red]")
        console.print(f"[yellow]Full traceback logged to {self.log_file}[/yellow]")
        
        return error_msg
        
    def handle_exception(self, exception, module=None, target=None):
        """Handle uncaught exceptions"""
        error_msg = self.log_error(exception, module, target)
        return {
            "status": "error",
            "module": module or "unknown",
            "target": target or "unknown",
            "message": error_msg
        }
        
    def tool_failure(self, tool_name, output, module=None, target=None):
        """Handle tool execution failures"""
        error_msg = f"Tool {tool_name} failed with output: {output[:200]}"
        self.log_error(Exception(error_msg), module, target)
        return {
            "status": "tool_failure",
            "tool": tool_name,
            "module": module or "unknown",
            "target": target or "unknown",
            "message": error_msg
        }