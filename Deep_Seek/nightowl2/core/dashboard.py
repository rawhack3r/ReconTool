from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TaskProgressColumn, TextColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
import psutil
import os
import time
from datetime import datetime
import threading

class NightOwlDashboard:
    def __init__(self):
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
        self.threat_intel = {}
        self.ai_insights = []
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
    
    def set_target_info(self, target, mode, target_type):
        self.target_info = {
            "target": target,
            "mode": mode,
            "type": target_type,
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
        self.start_time = datetime.now()
    
    def set_phases(self, phases):
        self.phase_status = {phase: {"status": "pending", "tools": []} for phase in phases}
    
    def start_phase(self, phase_idx):
        phase = list(self.phase_status.keys())[phase_idx]
        self.phase_status[phase]["status"] = "running"
    
    def complete_phase(self, phase_idx):
        phase = list(self.phase_status.keys())[phase_idx]
        self.phase_status[phase]["status"] = "completed"
    
    def start_tool(self, tool_name, description):
        phase = list(self.phase_status.keys())[-1]  # Current phase
        task_id = f"{phase}-{tool_name}"
        if task_id not in self.tool_progress:
            progress = Progress(
                TextColumn(f"[bold]{tool_name}[/]", width=20),
                BarColumn(bar_width=30),
                TaskProgressColumn()
            )
            task = progress.add_task(description, total=100)
            self.tool_progress[task_id] = {
                "progress": progress,
                "task": task,
                "start_time": datetime.now(),
                "status": "running"
            }
            self.phase_status[phase]["tools"].append(tool_name)
    
    def update_tool(self, tool_name, percentage, message=""):
        phase = list(self.phase_status.keys())[-1]  # Current phase
        task_id = f"{phase}-{tool_name}"
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["progress"].update(
                self.tool_progress[task_id]["task"],
                completed=percentage,
                description=message
            )
    
    def complete_tool(self, tool_name, summary):
        phase = list(self.phase_status.keys())[-1]  # Current phase
        task_id = f"{phase}-{tool_name}"
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["status"] = "completed"
            self.tool_progress[task_id]["end_time"] = datetime.now()
            duration = self.tool_progress[task_id]["end_time"] - self.tool_progress[task_id]["start_time"]
            self.tool_progress[task_id]["summary"] = f"{summary} (⏱️ {duration.total_seconds():.1f}s)"
    
    def tool_error(self, tool_name, error):
        phase = list(self.phase_status.keys())[-1]  # Current phase
        task_id = f"{phase}-{tool_name}"
        self.errors.append({
            "phase": phase,
            "tool": tool_name,
            "error": error,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["status"] = "error"
            self.tool_progress[task_id]["progress"].update(
                self.tool_progress[task_id]["task"],
                description=f"[red]ERROR: {error}[/]"
            )
    
    def add_threat_intel(self, source, data):
        self.threat_intel[source] = data
    
    def add_ai_insight(self, insight):
        self.ai_insights.append(insight)
    
    def render(self):
        # Header - System resources and target info
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
                    self.tool_progress.get(f"{phase}-{tool}", {}).get("progress", "")
                    for tool in status["tools"]
                ]
                phase_panel = Panel(
                    f"[bold]{phase}[/]\n" + "\n".join(tools),
                    border_style="yellow"
                )
                main_content.append(phase_panel)
        
        # Sidebar - Phase checklist and threat intel
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
        
        # Threat intelligence
        if self.threat_intel:
            intel_table = Table(show_header=False)
            for source, data in self.threat_intel.items():
                intel_table.add_row(source, f"{len(data.get('pulses', []))} pulses")
            sidebar_content.append(Panel(
                intel_table,
                title="[bold]THREAT INTELLIGENCE[/]",
                border_style="magenta"
            ))
        
        # AI insights
        if self.ai_insights:
            insights_panel = Panel(
                "\n".join([f"- {insight[:60]}..." for insight in self.ai_insights[:3]]),
                title="[bold]AI INSIGHTS[/]",
                border_style="blue"
            )
            sidebar_content.append(insights_panel)
        
        # Footer - Errors and overall progress
        footer_content = ""
        if self.errors:
            error_table = Table(title="Recent Errors")
            error_table.add_column("Phase", style="cyan")
            error_table.add_column("Tool")
            error_table.add_column("Error")
            error_table.add_column("Time")
            
            for error in self.errors[-3:]:
                error_table.add_row(
                    error["phase"],
                    error["tool"],
                    error["error"][:50] + ("..." if len(error["error"]) > 50 else ""),
                    error["timestamp"]
                )
            footer_content += str(error_table) + "\n\n"
        
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
    
    def show_success(self, message):
        self.console.print(Panel(message, style="bold green", title="Success"))
    
    def show_warning(self, message):
        self.console.print(Panel(message, style="bold yellow", title="Warning"))
    
    def show_error(self, message):
        self.console.print(Panel(message, style="bold red", title="Error"))
    
    def show_info(self, message):
        self.console.print(Panel(message, style="bold blue", title="Info"))