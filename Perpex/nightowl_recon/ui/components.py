# ui/components.py

from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import BarColumn, Progress

def create_header_panel(status: str, start_time: datetime, current_time: datetime) -> Panel:
    elapsed = current_time - start_time
    txt = Text(
        f"Status: {status}    Started: {start_time.strftime('%H:%M:%S')}    "
        f"Elapsed: {str(elapsed).split('.')[0]}",
        style="bold cyan"
    )
    return Panel(txt, style="bold white on blue")

def create_resource_panel(resource_usage: dict) -> Panel:
    cpu = resource_usage.get("cpu_percent", 0)
    mem = resource_usage.get("memory_percent", 0)
    net = resource_usage.get("network_mb", 0)
    txt = Text(f"CPU: {cpu:.0f}% | Mem: {mem:.0f}% | Net: {net:.1f}MB", style="green")
    return Panel(txt, title="Resources", border_style="green")

def create_target_panel(target: str, mode: str, overall_progress: float) -> Panel:
    table = Table.grid(expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")
    bar = Progress(
        "{task.percentage:>3.0f}%",
        BarColumn(bar_width=None),
        expand=True,
        transient=True
    )
    bar.add_task("", total=100, completed=overall_progress)
    table.add_row(f"[bold]Target:[/bold] {target}", f"[bold]Mode:[/bold] {mode}")
    table.add_row(bar, "")
    return Panel(table, title="Target", border_style="cyan")

def create_phase_panel(current_phase: int, total_phases: int, _unused=None) -> Panel:
    txt = Text(f"Phase {current_phase}/{total_phases}", style="magenta")
    return Panel(txt, title="Phase", border_style="magenta")

def create_tool_status_panel(scan_results: dict) -> Panel:
    table = Table(expand=True)
    table.add_column("Tool", style="bold")
    table.add_column("Items", justify="right")
    for tool, results in scan_results.items():
        count = len(results) if hasattr(results, "__len__") else "-"
        table.add_row(tool, str(count))
    return Panel(table, title="Tools", border_style="blue")

def create_results_panel(scan_results: dict) -> Panel:
    table = Table.grid(expand=True)
    for tool, results in scan_results.items():
        count = len(results) if hasattr(results, "__len__") else "-"
        table.add_row(f"[green]{tool}[/green]", f"{count}")
    return Panel(table, title="Results", border_style="green")

def create_error_panel(failed_tools: dict, scan_results: dict) -> Panel:
    if not failed_tools:
        body = Text("No errors.", style="green")
    else:
        body = Text()
        for tool, err in failed_tools.items():
            body.append(f"- {tool}: {err}\n", style="red")
    return Panel(body, title="Errors", border_style="red")

def create_summary_panel(stats: dict) -> Panel:
    """
    Footer summary panel. Expects stats keys:
      target, mode, current_phase, total_phases,
      completed_tools (int), failed_tools (int), elapsed_time, resource_usage
    """
    lines = []
    lines.append(f"Target: {stats.get('target')}")
    lines.append(f"Mode: {stats.get('mode')}")
    lines.append(f"Phase: {stats.get('current_phase')}/{stats.get('total_phases')}")
    completed = stats.get('completed_tools', 0)
    failed = stats.get('failed_tools', 0)
    lines.append(f"Completed Tools: {completed}")
    lines.append(f"Failed Tools: {failed}")
    lines.append(f"Elapsed: {stats.get('elapsed_time')}")
    resource = stats.get("resource_usage", {})
    cpu = resource.get("cpu_percent", 0)
    mem = resource.get("memory_percent", 0)
    net = resource.get("network_mb", 0)
    lines.append(f"CPU: {cpu:.0f}% | Mem: {mem:.0f}% | Net: {net:.1f}MB")
    body = Text("\n".join(lines), style="bold")
    return Panel(body, title="Summary", border_style="white")
