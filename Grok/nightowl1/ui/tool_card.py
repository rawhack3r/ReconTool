from rich.console import Console
from rich.panel import Panel

console = Console()

def display_tool_card(tool_name, status, progress, results):
    content = f"Tool: {tool_name}\nStatus: {status}\nProgress: {progress}%\nResults: {results}"
    panel = Panel(content, title=f"{tool_name} Status", border_style="blue")
    console.print(panel)