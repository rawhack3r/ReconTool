from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.live import Live

class NightOwlUI:
    def __init__(self):
        self.console = Console()
        self._live = None

    def show_banner(self):
        banner = Panel.fit(
            "[bold cyan]⚡ NightOwl Recon ⚡[/bold cyan]\n[green]n00bhack3r x ChatGPT[/green]",
            border_style="magenta"
        )
        self.console.print(banner)

    def log(self, msg: str):
        self.console.print(msg)

    def log_warn(self, msg: str):
        self.console.print(f"[yellow][!][/yellow] {msg}")

    def log_error(self, msg: str):
        self.console.print(f"[red][x][/red] {msg}")

    def log_success(self, msg: str):
        self.console.print(f"[green][✓][/green] {msg}")

    def phase_start(self, name: str):
        self.console.rule(f"[bold magenta]Phase: {name}[/bold magenta]")

    def phase_end(self, name: str):
        self.console.print(f"[green]Completed phase {name}[/green]")

    # future: live checklist panel updates...
