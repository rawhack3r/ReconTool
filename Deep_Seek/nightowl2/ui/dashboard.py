import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.style import Style

class NightOwlDashboard:
    def __init__(self, verbose=False):
        self.console = Console()
        self.layout = Layout()
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TextColumn("[blue]{task.completed}/{task.total}"),
            expand=True
        )
        self.verbose = verbose
        self.tool_outputs = {}
        self.current_tool = None
        self.setup_layout()
        
    def setup_layout(self):
        """Setup dashboard layout"""
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="progress", ratio=3),
            Layout(name="output", ratio=2)
        )
        self.layout["output"].visible = self.verbose
        
    def start(self):
        """Start the dashboard"""
        self.console.clear()
        self.console.print(Panel("🦉 NightOwl Reconnaissance Suite", 
                                style="bold blue", 
                                subtitle="Initializing..."))
        time.sleep(0.5)
        
    def display_header(self):
        """Display target information header"""
        header = Panel(
            f"[bold]Target:[/] {self.target} | [bold]Mode:[/] {self.mode} | [bold]Type:[/] {self.target_type}",
            style="bold green"
        )
        self.layout["header"].update(header)
        
    def set_target_info(self, target, mode, target_type):
        """Set target information"""
        self.target = target
        self.mode = mode
        self.target_type = target_type
        
    def set_phases(self, phases):
        """Set scan phases"""
        self.phases = phases
        self.phase_tasks = [self.progress.add_task(f"[cyan]{phase}", total=100) for phase in phases]
        
    def start_phase(self, phase_idx):
        """Start a new phase"""
        self.current_phase_idx = phase_idx
        self.console.print(f"\n[bold yellow]Starting phase: {self.phases[phase_idx]}[/]")
        self.current_tool = None
        self.tool_outputs = {}
        
    def complete_phase(self, phase_idx):
        """Complete current phase"""
        self.progress.update(self.phase_tasks[phase_idx], completed=100)
        self.console.print(f"[bold green]✓ Completed phase: {self.phases[phase_idx]}[/]")
        
    def start_tool(self, tool_name, description):
        """Start a new tool execution"""
        self.current_tool = tool_name
        self.tool_outputs[tool_name] = []
        self.console.print(f"[blue]• {tool_name}:[/] {description}")
        
    def complete_tool(self, tool_name, result):
        """Complete tool execution"""
        self.console.print(f"[green]  ✓ {tool_name}:[/] {result}")
        
    def tool_error(self, tool_name, error):
        """Report tool error"""
        self.console.print(f"[red]  ✗ {tool_name} error:[/] {error}")
        
    def show_tool_output(self, tool_name, output_line):
        """Display tool output in verbose mode"""
        if self.verbose and tool_name == self.current_tool:
            self.tool_outputs[tool_name].append(output_line)
            output_panel = self._format_output_panel()
            self.layout["output"].update(output_panel)
            
    def _format_output_panel(self):
        """Format tool output for display"""
        if not self.current_tool:
            return Panel("No active tool", title="Tool Output")
            
        output_text = "\n".join(self.tool_outputs[self.current_tool][-20:])  # Show last 20 lines
        return Panel(
            output_text,
            title=f"[bold]{self.current_tool} Output",
            border_style="yellow"
        )
        
    def show_info(self, message):
        """Display information message"""
        self.console.print(f"[cyan]ℹ {message}[/]")
        
    def show_warning(self, message):
        """Display warning message"""
        self.console.print(f"[yellow]⚠ {message}[/]")
        
    def show_error(self, message):
        """Display error message"""
        self.console.print(f"[red]✗ {message}[/]")
        
    def show_success(self, message):
        """Display success message"""
        self.console.print(f"[green]✓ {message}[/]")
        
    def update(self):
        """Update the dashboard display"""
        progress_panel = Panel(self.progress, title="Scan Progress", border_style="blue")
        self.layout["progress"].update(progress_panel)
        
        # Display the layout
        self.console.print(self.layout)
        
    def stop(self):
        """Stop the dashboard"""
        self.console.print("\n[bold green]Scan completed successfully![/]")