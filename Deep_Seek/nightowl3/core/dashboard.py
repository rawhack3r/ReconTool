import os
import time
import threading
import psutil
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TaskProgressColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.style import Style

class NightOwlDashboard:
    def __init__(self, verbose=False):
        self.console = Console()
        self.layout = Layout()
        self.resource_data = {"cpu": 0, "mem": 0, "net_sent": 0, "net_recv": 0}
        self.target_info = {}
        self.tool_progress = {}
        self.phase_status = {}
        self.errors = []
        self.start_time = None
        self.is_running = True
        self.overall_progress = 0
        self.verbose = verbose
        self.tool_install_status = {}
        self.init_layout()
        threading.Thread(target=self.monitor_resources, daemon=True).start()
    
    def init_layout(self):
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=7)
        )
        self.layout["body"].split_row(
            Layout(name="main", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
    
    def monitor_resources(self):
        net_io = psutil.net_io_counters()
        while self.is_running:
            self.resource_data = {
                "cpu": psutil.cpu_percent(),
                "mem": psutil.virtual_memory().percent,
                "net_sent": (psutil.net_io_counters().bytes_sent - net_io.bytes_sent) / 1024,
                "net_recv": (psutil.net_io_counters().bytes_recv - net_io.bytes_recv) / 1024
            }
            net_io = psutil.net_io_counters()
            time.sleep(1)
    
    def start(self):
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]NightOwl Reconnaissance Suite[/] - [green]Initializing...[/]",
            style="bold blue"
        ))
    
    def set_target_info(self, target, mode, target_type):
        self.target_info = {
            "target": target,
            "mode": mode,
            "type": target_type,
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        self.start_time = datetime.now()
    
    def set_phases(self, phases):
        self.phase_status = {phase: {"status": "pending"} for phase in phases}
    
    def start_phase(self, phase_idx):
        phase = list(self.phase_status.keys())[phase_idx]
        self.phase_status[phase]["status"] = "running"
        self.overall_progress = int((phase_idx / len(self.phase_status)) * 100)
    
    def complete_phase(self, phase_idx):
        phase = list(self.phase_status.keys())[phase_idx]
        self.phase_status[phase]["status"] = "completed"
        self.overall_progress = int(((phase_idx + 1) / len(self.phase_status)) * 100)
    
    def start_tool(self, tool, description):
        """Record the start of a tool and display in dashboard"""
        if tool not in self.tool_progress:
            progress = Progress(
                TextColumn(f"[bold]{tool}[/]", width=20),
                BarColumn(bar_width=30),
                TaskProgressColumn()
            )
            task = progress.add_task(description, total=100)
            self.tool_progress[tool] = {
                "progress": progress,
                "task": task,
                "start_time": datetime.now(),
                "status": "running",
                "output": []
            }
    
    def skip_tool(self, tool, reason):
        """Mark a tool as skipped and display reason"""
        self.tool_progress[tool] = {
            "status": "skipped",
            "reason": reason
        }
    
    def update_tool(self, tool, percentage, message=""):
        """Update progress percentage for a tool"""
        if tool in self.tool_progress and "progress" in self.tool_progress[tool]:
            self.tool_progress[tool]["progress"].update(
                self.tool_progress[tool]["task"],
                completed=percentage,
                description=message
            )
    
    def add_tool_output(self, tool, output):
        """Add output line for a tool"""
        if tool in self.tool_progress and "output" in self.tool_progress[tool]:
            self.tool_progress[tool]["output"].append(output)
            if self.verbose:
                self.console.print(f"[dim][{tool}][/] {output}")
    
    def complete_tool(self, tool, summary):
        """Mark a tool as completed and record result summary"""
        if tool in self.tool_progress:
            self.tool_progress[tool]["status"] = "completed"
            self.tool_progress[tool]["end_time"] = datetime.now()
            duration = self.tool_progress[tool]["end_time"] - self.tool_progress[tool]["start_time"]
            self.tool_progress[tool]["summary"] = f"{summary} (⏱️ {duration.total_seconds():.1f}s)"
    
    def tool_error(self, tool, error):
        """Record a tool error and display in dashboard"""
        if tool in self.tool_progress:
            self.tool_progress[tool]["status"] = "error"
            self.tool_progress[tool]["progress"].update(
                self.tool_progress[tool]["task"],
                description=f"[red]ERROR: {error}[/]"
            )
        else:
            self.tool_progress[tool] = {
                "status": "error",
                "error": error
            }
        self.errors.append({
            "tool": tool,
            "error": error,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    def show_info(self, message):
        self.console.print(f"[cyan][ℹ][/] {message}")
    
    def show_warning(self, message):
        self.console.print(f"[yellow][⚠][/] {message}")
    
    def show_error(self, message):
        self.console.print(f"[red][✗][/] {message}")
    
    def show_success(self, message):
        self.console.print(f"[green][✓][/] {message}")
    
    def render(self):
        # Header
        header_content = Text.assemble(
            ("🦉 NightOwl ", "bold cyan"),
            (f"Target: [bold]{self.target_info.get('target', 'N/A')}[/] | "),
            (f"Mode: [bold]{self.target_info.get('mode', 'light')}[/] | "),
            (f"Started: [bold]{self.target_info.get('start_time', 'N/A')}[/]")
        )
        resources = (
            f"CPU: {self.resource_data['cpu']}% | "
            f"MEM: {self.resource_data['mem']}% | "
            f"NET: ▲{self.resource_data['net_sent']:.1f}KB/s ▼{self.resource_data['net_recv']:.1f}KB/s"
        )
        header_panel = Panel(
            header_content,
            subtitle=resources,
            title="[bold]RECON IN PROGRESS[/]",
            border_style="cyan"
        )
        
        # Main content - Tool progress
        main_content = []
        for phase, status in self.phase_status.items():
            if status["status"] == "running":
                tools = [
                    self.tool_progress.get(tool, {}).get("progress", "")
                    for tool in status.get("tools", [])
                ]
                phase_panel = Panel(
                    f"[bold]{phase}[/]\n" + "\n".join(tools),
                    border_style="yellow"
                )
                main_content.append(phase_panel)
        
        # Sidebar - Phase checklist and tool status
        sidebar_content = []
        
        # Phase checklist
        phase_table = Table(show_header=False)
        for phase, status in self.phase_status.items():
            status_icon = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅"
            }.get(status["status"], "❓")
            phase_table.add_row(f"{status_icon} {phase}")
        sidebar_content.append(Panel(
            phase_table,
            title="[bold]WORKFLOW PROGRESS[/]",
            border_style="green"
        ))
        
        # Tool status
        tool_status_table = Table(title="Tool Status", show_header=True)
        tool_status_table.add_column("Tool")
        tool_status_table.add_column("Status")
        tool_status_table.add_column("Result")
        
        for tool, data in self.tool_progress.items():
            status = data.get("status", "unknown")
            status_text = {
                "running": "[yellow]RUNNING[/]",
                "completed": "[green]COMPLETED[/]",
                "skipped": "[dim]SKIPPED[/]",
                "error": "[red]ERROR[/]"
            }.get(status, status)
            
            result = data.get("summary", data.get("reason", ""))
            tool_status_table.add_row(tool, status_text, result[:50] + ("..." if len(result) > 50 else ""))
        
        sidebar_content.append(Panel(
            tool_status_table,
            title="[bold]TOOL STATUS[/]",
            border_style="blue"
        ))
        
        # Footer - Recent errors
        footer_content = ""
        if self.errors:
            error_table = Table(title="Recent Errors")
            error_table.add_column("Tool", style="cyan")
            error_table.add_column("Error")
            error_table.add_column("Time")
            
            for error in self.errors[-3:]:
                error_table.add_row(
                    error["tool"],
                    error["error"][:50] + ("..." if len(error["error"]) > 50 else ""),
                    error["timestamp"]
                )
            footer_content += str(error_table) + "\n\n"
        
        # Overall progress
        overall_progress = Progress(
            TextColumn("[bold]OVERALL PROGRESS[/]", justify="right"),
            BarColumn(bar_width=50),
            TaskProgressColumn()
        )
        task = overall_progress.add_task("", total=100)
        overall_progress.update(task, completed=self.overall_progress)
        footer_content += str(overall_progress)
        
        footer_panel = Panel(
            footer_content,
            title="[bold]SYSTEM STATUS[/]",
            border_style="red" if self.errors else "blue"
        )
        
        # Assemble layout
        self.layout["header"].update(header_panel)
        self.layout["main"].update(Layout(Columns(main_content)))
        self.layout["sidebar"].update(Layout(Columns(sidebar_content)))
        self.layout["footer"].update(footer_panel)
        
        return self.layout
    
    def update(self):
        self.console.print(self.layout)
    
    def stop(self):
        self.is_running = False
        duration = datetime.now() - self.start_time
        self.console.print(
            Panel(f"[green]Scan completed in {duration} [/]", 
            title="NightOwl Finished", 
            style="bold green")
        )