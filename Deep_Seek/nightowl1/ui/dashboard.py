# ... (previous imports) ...
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table, Column
from rich.progress import Progress, BarColumn, TextColumn

class NightOwlDashboard:
    # ... (previous methods) ...
    
    def _create_layout(self):
        self.layout = Layout()
        
        # Header section
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1)
        )
        
        # Main section split
        self.layout["main"].split_row(
            Layout(name="work_area", ratio=3),
            Layout(name="phase_area", ratio=1)
        )
        
        # Initialize panels
        self.header_panel = Panel("", title="System Resources", style="header")
        self.work_panel = Panel("", title="[bold]Active Operations[/]", padding=(1, 2))
        self.phase_panel = Panel("", title="[bold]Workflow Progress[/]", padding=(1, 2))
        
        # Update layout
        self.layout["header"].update(self.header_panel)
        self.layout["work_area"].update(self.work_panel)
        self.layout["phase_area"].update(self.phase_panel)
        
    def set_current_phase(self, phase_index):
        self.current_phase = phase_index
        self._update_phase_display()
        
    def start_tool(self, tool_name, description):
        progress = Progress(
            TextColumn(f"[tool]{tool_name}[/]", width=20),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[info]{task.description}", overflow="ellipsis"),
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
        
    def _update_phase_display(self):
        if not hasattr(self, 'phases'):
            return
            
        table = Table(
            Column("Phase", style="phase_header"),
            Column("Status", style="status_header"),
            expand=True
        )
        
        for idx, phase in enumerate(self.phases):
            status = "pending"
            if idx < self.current_phase:
                status = "completed"
            elif idx == self.current_phase:
                status = "running"
                
            if status == "pending":
                icon, style = "⏳", "phase_pending"
            elif status == "completed":
                icon, style = "✅", "phase_completed"
            else:
                icon, style = "🦉", "phase_active"
                
            table.add_row(phase['name'], f"{icon} [bold]{status.capitalize()}[/]", style=style)
            
        self.phase_panel.renderable = table