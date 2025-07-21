from rich.console import Console
from rich.table import Table
from datetime import datetime

console = Console()

class ReconErrorHandler:
    def __init__(self):
        self.errors = []
    
    def log(self, tool: str, error: str):
        """Record errors with timestamp"""
        self.errors.append({
            "tool": tool,
            "error": error,
            "time": datetime.now().isoformat()
        })
    
    def report(self):
        """Print beautiful error table"""
        if not self.errors:
            return
            
        table = Table(title="[red]ERROR SUMMARY", show_header=True)
        table.add_column("Tool", style="cyan")
        table.add_column("Error", style="yellow")
        table.add_column("Time", style="magenta")
        
        for err in self.errors[-5:]:  # Show last 5 errors
            table.add_row(err["tool"], err["error"], err["time"])
        
        console.print(table)