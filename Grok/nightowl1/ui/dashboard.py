from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress
import time

console = Console()

def display_dashboard(status, resources, target_info, phases, tools):
    banner = Panel(
        f"[bold]NightOwl Recon[/bold] - {status}\n"
        f"CPU: {resources['cpu']:.1f}% | RAM: {resources['ram']:.1f}% | Network: {resources['network']:.1f} KB/s\n"
        f"Target: {target_info['domain']} | Mode: {target_info['mode']} | Type: {target_info['type']}",
        title="NightOwl Status",
        border_style="blue"
    )
    console.print(banner)

    phase_table = Table(title="Workflow Phases")
    phase_table.add_column("Phase", style="cyan")
    phase_table.add_column("Status", style="green")
    for phase, status in phases.items():
        phase_table.add_row(phase, status)
    console.print(phase_table)

    tool_table = Table(title="Tool Execution")
    tool_table.add_column("Tool", style="cyan")
    tool_table.add_column("Status", style="green")
    tool_table.add_column("Progress", style="yellow")
    tool_table.add_column("Start Time", style="magenta")
    tool_table.add_column("Duration", style="blue")
    tool_table.add_column("Results", style="white")
    for tool in tools:
        start_time = time.strftime("%H:%M:%S", time.localtime(tool.get('start_time', 0))) if tool.get('start_time') else "-"
        duration = f"{tool.get('duration', 0):.2f}s" if tool.get('duration') else "-"
        results = tool.get('results', "-")
        tool_table.add_row(
            tool['name'],
            tool['status'],
            f"{tool['progress']}%",
            start_time,
            duration,
            results
        )
    console.print(tool_table)