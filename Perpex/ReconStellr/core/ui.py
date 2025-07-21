from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import psutil, time, threading

console = Console()

def watch_resources():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return f"[yellow]CPU:[/yellow] {cpu}% [blue]RAM:[/blue] {ram}%"

def draw_banner(target, mode):
    banner = (
        "[bold magenta]ReconStellr 🚀[/bold magenta] " 
        f"| [cyan]Target:[/cyan] {target} | [yellow]Mode:[/yellow] {mode}"
        "\n[bold]n00bh4ck3r started / starting recon[/bold]"
    )
    console.print(Panel(banner, title="Fixed Banner", border_style="magenta"))
    # Display resource monitor (update in a thread if you wish)

def show_checklist(steps_status, phase_name):
    table = Table(title=f"[green]Phase: {phase_name} Progress", show_lines=True)
    table.add_column("Step")
    table.add_column("Status")
    for step, status in steps_status.items():
        icon = "✅" if status == "completed" else "❌" if status == "failed" else "⏳"
        table.add_row(step, icon)
    console.print(table)

def print_phase_status(phase_name, completed, total):
    percent = int((completed / total) * 100)
    console.print(f"[bold]{phase_name}[/bold]: {percent}% done")
