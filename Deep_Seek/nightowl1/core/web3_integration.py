import time
import threading
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table, Column
from rich.live import Live
from rich.text import Text
from rich.layout import Layout
from .theme import NIGHTOWL_THEME

class NightOwlDashboard:
    def __init__(self):
        self.console = Console(theme=NIGHTOWL_THEME)
        self.live = None
        self.layout = None
        self.progress_bars = {}
        self.current_phase = 0
        self.resource_thread = None
        self.running = False
        self.is_running = False
        
    def display_header(self):
        title = Text("🦉 NIGHT OWL RECONNAISSANCE SUITE", justify="center", style="banner")
        subtitle = Text("Comprehensive Attack Surface Discovery", justify="center", style="subtitle")
        self.console.print(Panel(title, subtitle=subtitle, style="header"))
        
    def start(self):
        self.is_running = True
        self._create_layout()
        self.live = Live(self.layout, refresh_per_second=10, console=self.console)
        self.live.__enter__()
        return self
        
    def stop(self):
        self.is_running = False
        if self.live:
            self.live.__exit__(None, None, None)
            
    def set_target_info(self, target, mode, target_type):
        self.target = target
        self.mode = mode
        self.target_type = target_type
        self._update_header()
        
    def set_phases(self, phases):
        self.phases = phases
        self.phase_status = ["pending"] * len(phases)
        self._update_phase_display()
        
    def set_current_phase(self, phase_index):
        self.current_phase = phase_index
        if phase_index < len(self.phase_status):
            self.phase_status[phase_index] = "running"
        self._update_phase_display()
        
    def complete_phase(self, phase_index):
        if phase_index < len(self.phase_status):
            self.phase_status[phase_index] = "completed"
        self._update_phase_display()
        
    def start_tool(self, tool_name, description):
        progress = Progress(
            TextColumn(f"[tool_name]{tool_name}[/]", width=20),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[description]{task.description}", overflow="ellipsis"),
            expand=True
        )
        task_id = progress.add_task(description, total=100)
        self.progress_bars[tool_name] = {
            'progress': progress,
            'task_id': task_id,
            'start_time': time.time(),
            'status': 'running'
        }
        self._update_tools_display()
        
    def update_tool_progress(self, tool_name, percentage, message=""):
        if tool_name in self.progress_bars:
            progress = self.progress_bars[tool_name]['progress']
            task_id = self.progress_bars[tool_name]['task_id']
            progress.update(task_id, completed=percentage, description=message)
            self._update_tools_display()
            
    def complete_tool(self, tool_name, summary, duration):
        if tool_name in self.progress_bars:
            progress = self.progress_bars[tool_name]['progress']
            task_id = self.progress_bars[tool_name]['task_id']
            progress.update(task_id, completed=100, description=summary)
            self.progress_bars[tool_name]['duration'] = duration
            self.progress_bars[tool_name]['status'] = 'completed'
            self._update_tools_display()
            
    def tool_error(self, tool_name, error_message):
        if tool_name in self.progress_bars:
            progress = self.progress_bars[tool_name]['progress']
            task_id = self.progress_bars[tool_name]['task_id']
            progress.update(task_id, description=f"[error]ERROR: {error_message}[/]")
            self.progress_bars[tool_name]['status'] = 'error'
            self._update_tools_display()
            
    def skip_tool(self, tool_name):
        self.progress_bars[tool_name] = {
            'status': 'skipped',
            'message': 'Skipped (already completed)'
        }
        self._update_tools_display()
            
    def update_resource_usage(self, cpu, memory, network_sent, network_recv):
        self.resource_usage = (
            f"CPU: {cpu}% | "
            f"RAM: {memory}% | "
            f"NET: ▲{network_sent/1024:.1f}KB/s ▼{network_recv/1024:.1f}KB/s"
        )
        self._update_resource_display()
        
    def show_success(self, message):
        self.console.print(Panel(message, title="[success]Success[/]", style="success"))
        
    def show_warning(self, message):
        self.console.print(Panel(message, title="[warning]Warning[/]", style="warning"))
        
    def show_error(self, message):
        self.console.print(Panel(message, title="[error]Error[/]", style="error"))
        
    def _create_layout(self):
        # Create main layout structure
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        self.layout["main"].split_row(
            Layout(name="work_area", ratio=3),
            Layout(name="phase_area", ratio=1)
        )
        
        # Initialize panels
        self.header_panel = Panel("", title="System Resources", style="header_panel")
        self.resource_panel = Panel("", style="resource_panel")
        self.work_panel = Panel("", title="[bold]Active Operations[/]", style="work_panel")
        self.phase_panel = Panel("", title="[bold]Workflow Progress[/]", style="phase_panel")
        
        # Update layout
        self.layout["header"].update(self.header_panel)
        self.layout["work_area"].update(self.work_panel)
        self.layout["phase_area"].update(self.phase_panel)
        
        # Initial content
        self._update_header()
        self._update_resource_display()
        self._update_tools_display()
        self._update_phase_display()
        
    def _update_header(self):
        title = Text(f"Target: [target]{self.target}[/] | Mode: [mode]{self.mode}[/] | Type: [type]{self.target_type}[/]", style="header_text")
        self.header_panel.renderable = title
        
    def _update_resource_display(self):
        if hasattr(self, 'resource_usage'):
            self.resource_panel.renderable = self.resource_usage
            
    def _update_tools_display(self):
        if not self.progress_bars:
            self.work_panel.renderable = Panel("No active operations", style="empty")
            return
            
        grid = Table.grid(expand=True)
        for tool, data in self.progress_bars.items():
            if data['status'] == 'skipped':
                grid.add_row(f"[skipped]⏩ {tool}: {data['message']}[/]")
            elif 'progress' in data:
                grid.add_row(data['progress'])
                if 'duration' in data:
                    grid.add_row(f"⏱️ [dim]Completed in {data['duration']:.2f}s[/]")
            elif data['status'] == 'error':
                grid.add_row(f"[error]❌ {tool}: Failed[/]")
        self.work_panel.renderable = grid
        
    def _update_phase_display(self):
        if not hasattr(self, 'phases'):
            return
            
        table = Table(
            Column(header="Phase", style="phase_header"),
            Column(header="Status", style="status_header"),
            expand=True
        )
        
        for idx, phase in enumerate(self.phases):
            status = self.phase_status[idx]
            if status == "pending":
                icon, style = "⏳", "phase_pending"
            elif status == "completed":
                icon, style = "✅", "phase_completed"
            else:  # running
                icon, style = "🦉", "phase_active"
                
            table.add_row(phase['name'], f"{icon} [bold]{status.capitalize()}[/]", style=style)
            
        self.phase_panel.renderable = table