import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.style import Style

console = Console()

class ProgressTracker:
    def __init__(self):
        self.start_time = time.time()
        self.current_target = None
        self.module_progress = {}
        self.errors = []
        self.target_count = 0
        self.completed_targets = 0
        
        # Progress display
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn()
        )
        
        # Live display
        self.live = Live(console=console, refresh_per_second=10, screen=False)
        self.live.start()
    
    def start_scan(self, target_count):
        self.target_count = target_count
        self.scan_task = self.progress.add_task(
            f"[cyan]Scanning {target_count} targets...", total=target_count
        )
        self._update_display()
    
    def start_target(self, target):
        self.current_target = target
        self.completed_targets += 1
        self.target_task = self.progress.add_task(
            f"[green]Processing {target}", total=100
        )
        self.module_progress = {}
        self._update_display()
    
    def start_module(self, module_name):
        self.module_progress[module_name] = {
            'start_time': time.time(),
            'progress': 0,
            'completed': False,
            'results': 0
        }
        self._update_display()
    
    def update_module(self, module_name, progress):
        if module_name in self.module_progress:
            self.module_progress[module_name]['progress'] = progress
            self._update_display()
    
    def complete_module(self, module_name, result_count=None):
        if module_name in self.module_progress:
            self.module_progress[module_name]['progress'] = 100
            self.module_progress[module_name]['completed'] = True
            if result_count is not None:
                self.module_progress[module_name]['results'] = result_count
            self._update_display()
    
    def add_error(self, error_message):
        self.errors.append(error_message)
        self._update_display()
    
    def _build_scan_status(self):
        status = f"Targets: [bold]{self.completed_targets}/{self.target_count}[/bold] completed\n"
        
        if self.current_target:
            status += f"\nCurrent: [bold]{self.current_target}[/bold]\n"
            for module, data in self.module_progress.items():
                status += f"\n[cyan]{module.capitalize()}:[/cyan] "
                if data.get('completed'):
                    status += "[green]✓ Completed[/green]"
                    if data['results'] > 0:
                        status += f" ([yellow]{data['results']}[/yellow] results)"
                else:
                    status += f"[yellow]{data['progress']}%[/yellow]"
        
        if self.errors:
            status += "\n\n[red]Errors:[/red]"
            for error in self.errors[-3:]:
                status += f"\n- {error}"
        
        return status
    
    def _update_display(self):
        # Create layout
        grid = Table.grid(expand=True)
        grid.add_column(width=35)
        grid.add_column(width=65)
        
        # Build panels
        status_panel = Panel(
            self._build_scan_status(),
            title="Scan Status",
            border_style="green"
        )
        
        grid.add_row(status_panel)
        self.live.update(grid)
    
    def complete_target(self, target):
        self.progress.update(self.target_task, completed=100)
        self._update_display()
    
    def complete_scan(self):
        self.live.stop()
        console.print(f"\n[bold green]✓ Scan completed in {time.time() - self.start_time:.2f} seconds[/bold green]")
    
    def report_generated(self, report_path):
        console.print(f"\n[bold]📊 Report generated:[/bold] [cyan]{report_path}[/cyan]")

def display_banner():
    console.print("\n[bold blue]========================================")
    console.print("    R E C O N X   v2.0")
    console.print("  Professional Reconnaissance Suite")
    console.print("========================================\n")