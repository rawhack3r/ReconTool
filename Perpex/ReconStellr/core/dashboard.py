import psutil
import time
from threading import Thread
from rich.live import Live
from rich.panel import Panel

def show_live_dashboard(target, mode, status_cb, duration=9999):
    def resource_line():
        return f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%"
    
    with Live(refresh_per_second=1) as live:
        for _ in range(duration):
            panel = Panel(
                f"[bold magenta]ReconStellr Live[/bold magenta]\n"
                f"[cyan]Target:[/cyan] {target} [yellow]Mode:[/yellow] {mode}\n"
                f"{status_cb()}",
                title=resource_line()
            )
            live.update(panel)
            time.sleep(1)
