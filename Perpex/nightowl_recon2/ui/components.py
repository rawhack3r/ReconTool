from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import DOUBLE, ROUNDED
from rich.console import Group

OWL, CPU, RAM, NET = "🦉", "🖥️", "💾", "🌐"
CHECK, FAIL, TOOL = "✅", "❌", "🛠️"
ERROR, RESULT = "⚠️", "📊"

def create_header_panel(status, start, now) -> Panel:
    title = f"{OWL} [bold magenta]NightOwl Recon"
    elapsed = str(now - start).split(".")[0]
    txt = Text.assemble(f"{status} | Started: {start:%H:%M:%S} | Elapsed: {elapsed}", style="bold cyan")
    return Panel(txt, title=title, border_style="bright_magenta", box=DOUBLE)

def create_tool_status_panel(scan_results) -> Panel:
    table = Table(expand=True, box=ROUNDED, border_style="bright_yellow")
    table.add_column("Tool", style="bold white")
    table.add_column("Items", style="bold green", justify="right")
    for t, lst in scan_results.items():
        cnt = len(lst) if hasattr(lst, "__len__") else "-"
        icon = CHECK if cnt and int(cnt)>0 else TOOL
        table.add_row(f"{icon} {t}", str(cnt))
    return Panel(table, title="🛠️ Tools", border_style="bright_yellow")

def create_results_panel(scan_results, tool_stats={}) -> Panel:
    table = Table.grid(expand=True, padding=(0,1))
    table.add_column("Tool", style="bold white")
    table.add_column("Results", justify="right", style="bold green")
    table.add_column("Time", justify="right", style="yellow")
    for t in scan_results.keys():
        cnt = len(scan_results.get(t,[]))
        tm = "-"
        s = tool_stats.get(t)
        if isinstance(s, dict):
            tm = f"{s.get('time',0):.0f}s"
        table.add_row(f"{RESULT} {t}", str(cnt), tm)
    return Panel(table, title="📊 Results", border_style="bright_green", box=ROUNDED)

def create_error_panel(failed_tools, scan_results) -> Panel:
    if not failed_tools:
        b = Text("No errors.", style="bold green")
    else:
        b = Text()
        for t, e in failed_tools.items():
            b.append(f"{ERROR} {t}: {e}\n", style="bold bright_red")
    return Panel(b, title="⚠️ Errors", border_style="bright_red", box=ROUNDED)

def create_footer_panel(stats) -> Panel:
    summary = Text()
    summary.append(f"Target: {stats['target']}\n", style="bold green")
    summary.append(f"Mode: {stats['mode']}\n", style="bold blue")
    summary.append(f"Completed: {stats['completed_tools']}  ", style="bold green")
    summary.append(f"Failed: {stats['failed_tools']}\n", style="bold red")
    summary.append(f"Merged: {stats['merged_subdomains']}  ", style="bold magenta")
    summary.append(f"Live: {stats['live_hosts']}\n", style="bold cyan")
    summary.append(f"Elapsed: {stats['elapsed_time']}\n", style="bold yellow")
    extra = Text("NightOwl Recon: FUTURE-READY. ALL SYSTEMS OPERATIONAL.", style="bold bright_cyan")
    return Panel(Group(summary, Text(), extra), title="🧠 Intelligence Summary", border_style="bright_cyan", box=DOUBLE)
