from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
import time

class NightOwlDashboard:
    def __init__(self, verbose=False):
        self.console = Console()
        self.verbose = verbose
        self.progress = None
        self.live = None
        self.table = None
        self.task_ids = {}
        self.phase_progress = None
        self.current_phase = 0
        self.phases = [
            "Initialization",
            "Subdomain Enumeration",
            "Live Host Checking",
            "Network Scanning",
            "Content Discovery",
            "Information Gathering",
            "Vulnerability Scanning",
            "Mobile Analysis",
            "Analysis & Reporting"
        ]
    
    def start(self):
        self.console.clear()
        self.console.print(Panel(Text("NightOwl Reconnaissance Tool", justify="center", style="bold blue"), width=80))
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            transient=True,
            console=self.console
        )
        self.live = Live(self.progress, refresh_per_second=10, console=self.console)
        self.live.__enter__()
    
    def stop(self):
        if self.live:
            self.live.__exit__(None, None, None)
    
    def set_target_info(self, target, mode, target_type):
        self.target = target
        self.mode = mode
        self.target_type = target_type
        self.console.print(f"[bold]Target:[/bold] {target}")
        self.console.print(f"[bold]Mode:[/bold] {mode}")
        self.console.print(f"[bold]Type:[/bold] {target_type}")
    
    def start_phase(self, phase_index):
        self.current_phase = phase_index
        self.console.print(f"\n[bold green]Phase {phase_index+1}: {self.phases[phase_index]}[/bold green]")
        self.phase_progress = self.progress.add_task(f"{self.phases[phase_index]}", total=100)
    
    def complete_phase(self, phase_index):
        self.progress.update(self.phase_progress, completed=100, visible=False)
        self.console.print(f"[bold green]✓ Phase {phase_index+1} completed![/bold green]")
    
    def start_tool(self, tool, description):
        task_id = self.progress.add_task(f"[cyan]{tool}[/cyan]: {description}", total=100)
        self.task_ids[tool] = task_id
        return task_id
    
    def complete_tool(self, tool, result):
        if tool in self.task_ids:
            self.progress.update(self.task_ids[tool], completed=100, visible=False)
            self.console.print(f"[green]✓ {tool}[/green]: {result}")
    
    def skip_tool(self, tool, reason):
        self.console.print(f"[yellow]⦸ {tool} skipped: {reason}[/yellow]")
    
    def tool_error(self, tool, error):
        if tool in self.task_ids:
            self.progress.update(self.task_ids[tool], completed=100, visible=False)
        self.console.print(f"[red]✗ {tool} error: {error}[/red]")
    
    def show_info(self, message):
        self.console.print(f"[blue][*][/blue] {message}")
    
    def show_warning(self, message):
        self.console.print(f"[yellow][!][/yellow] {message}")
    
    def show_error(self, message):
        self.console.print(f"[red][!][/red] {message}")
    
    def show_success(self, message):
        self.console.print(f"[green][+][/green] {message}")
    
    def update_progress(self, tool, progress):
        if tool in self.task_ids:
            self.progress.update(self.task_ids[tool], completed=progress)