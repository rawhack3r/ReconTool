import time
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from core.monitor import ResourceMonitor

console = Console()

class ProgressTracker:
    def __init__(self):
        self.start_time = time.time()
        self.current_target = None
        self.module_progress = {}
        self.errors = []
        self.resource_monitor = ResourceMonitor()
        
        # Progress display
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn()
        )
        
        # Live display
        self.live = Live(console=console, refresh_per_second=10)
        self.live.start()
    
    def start_scan(self, target_count):
        self.scan_task = self.progress.add_task(
            f"[cyan]Scanning {target_count} targets...", total=target_count
        )
        self.status_table = Table.grid(padding=1)
        self.status_table.add_row(
            Panel(self._build_system_stats(), title="System Resources"),
            Panel(self._build_scan_status(), title="Scan Status")
        )
        self.live.update(self.status_table)
    
    def start_target(self, target, index):
        self.current_target = target
        self.target_task = self.progress.add_task(
            f"[green]Processing {target}", total=100
        )
        self.progress.update(self.scan_task, advance=1)
        self.module_progress = {}
    
    def start_module(self, module_name):
        self.module_progress[module_name] = {
            'start_time': time.time(),
            'progress': 0
        }
        self._update_display()
    
    def update_module(self, module_name, progress):
        self.module_progress[module_name]['progress'] = progress
        self._update_display()
    
    def complete_module(self, module_name, result_count=None):
        if module_name in self.module_progress:
            self.module_progress[module_name]['progress'] = 100
            self.module_progress[module_name]['completed'] = True
            if result_count is not None:
                self.module_progress[module_name]['results'] = result_count
            self._update_display()
    
    def add_error(self, target, error_message):
        self.errors.append(f"{target}: {error_message}")
        self._update_display()
    
    def _build_system_stats(self):
        stats = self.resource_monitor.get_system_stats()
        peak = self.resource_monitor.get_peak_usage()
        
        return (
            f"CPU Usage: {stats['cpu_usage']}%\n"
            f"RAM Usage: {stats['ram_usage']}%\n"
            f"Peak CPU: {peak['max_cpu']}%\n"
            f"Peak RAM: {peak['max_ram']:.1f} MB\n"
            f"Uptime: {stats['uptime']:.1f}s"
        )
    
    def _build_scan_status(self):
        if not self.current_target:
            return "No active target"
        
        status = f"Target: [bold]{self.current_target}[/bold]\n"
        for module, data in self.module_progress.items():
            status += f"\n[cyan]{module.capitalize()}:[/cyan] "
            if data.get('completed'):
                status += "[green]✓ Completed[/green]"
                if 'results' in data:
                    status += f" ({data['results']} results)"
            else:
                status += f"[yellow]{data['progress']}%[/yellow]"
        
        if self.errors:
            status += "\n\n[red]Errors:[/red]"
            for error in self.errors[-3:]:
                status += f"\n- {error}"
        
        return status
    
    def _update_display(self):
        self.status_table = Table.grid(padding=1)
        self.status_table.add_row(
            Panel(self._build_system_stats(), title="System Resources"),
            Panel(self._build_scan_status(), title="Scan Status")
        )
        self.live.update(self.status_table)
    
    def complete_target(self, target):
        self.progress.update(self.target_task, completed=100)
        self.current_target = None
        self._update_display()
    
    def complete_scan(self):
        self.live.stop()
        console.print(f"\n[bold green]Scan completed in {time.time() - self.start_time:.2f} seconds[/bold green]")
    
    def report_generated(self, report_path):
        console.print(f"\n[bold]Report generated:[/bold] [cyan]{report_path}[/cyan]")