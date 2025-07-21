from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from datetime import datetime

class ToolCard:
    def __init__(self, tool_name, description):
        self.tool_name = tool_name
        self.description = description
        self.start_time = datetime.now()
        self.end_time = None
        self.progress = 0
        self.status = "pending"  # pending, running, completed, error
        self.result = None
        self.error = None
    
    def start(self):
        self.status = "running"
        self.start_time = datetime.now()
    
    def update(self, progress, message=""):
        self.progress = progress
        self.message = message
    
    def complete(self, result):
        self.status = "completed"
        self.end_time = datetime.now()
        self.result = result
        self.progress = 100
    
    def error(self, error_message):
        self.status = "error"
        self.end_time = datetime.now()
        self.error = error_message
        self.progress = 100
    
    def render(self):
        """Render the tool card as a Rich Panel"""
        status_colors = {
            "pending": "dim",
            "running": "bold yellow",
            "completed": "bold green",
            "error": "bold red"
        }
        
        title = Text.assemble(
            ("🛠️  ", "bold"),
            (self.tool_name, "bold cyan"),
            f" - {self.description}",
            style=status_colors[self.status]
        )
        
        content = []
        
        # Status and timing
        if self.status == "running":
            content.append(f"⏱️ Started: {self.start_time.strftime('%H:%M:%S')}")
            content.append(f"📈 Progress: {self.progress}%")
            if hasattr(self, 'message'):
                content.append(f"💬 {self.message}")
        elif self.status == "completed":
            duration = (self.end_time - self.start_time).total_seconds()
            content.append(f"✅ Completed in {duration:.2f}s")
            if self.result:
                content.append(self._format_result())
        elif self.status == "error":
            content.append(f"❌ Failed: {self.error}")
        
        # Result summary
        if self.result and self.status == "completed":
            content.append("")
            content.append("[bold]Results:[/]")
            content.append(self._format_result())
        
        return Panel(
            "\n".join(content),
            title=title,
            border_style=status_colors[self.status]
        )
    
    def _format_result(self):
        """Format result summary based on tool type"""
        if "subdomains" in self.result:
            count = len(self.result["subdomains"])
            return f"🌐 Found {count} subdomains"
        elif "vulnerabilities" in self.result:
            count = len(self.result["vulnerabilities"])
            return f"⚠️ Found {count} vulnerabilities"
        elif "secrets" in self.result:
            count = len(self.result["secrets"])
            return f"🔑 Found {count} secrets"
        return "Task completed successfully"