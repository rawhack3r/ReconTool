import asyncio
from datetime import datetime
from rich.live import Live
from rich.layout import Layout
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from rich.box import DOUBLE

from .components import (
    create_header_panel,
    create_footer_panel,
    create_tool_status_panel,
    create_results_panel,
    create_error_panel,
)


def create_verbose_panel(logs, stats):
    """
    Builds the central verbose panel, including a status bar
    showing target, phase, live hosts, and resource usage.
    """
    status = Text.assemble(
        ("🦉 ", "bold magenta"),
        (stats["target"], "bold magenta"),
        ("  ┃  Phase:", "cyan"),
        (f" {stats['current_phase']}/{stats['total_phases']}", "yellow"),
        ("  ┃  Live:", "cyan"),
        (f" {stats['live_hosts']}", "bright_green"),
        ("  ┃  CPU:", "cyan"),
        (f" {stats['resource_usage']['cpu_percent']:.0f}%", "bright_cyan"),
        ("  ┃  Mem:", "cyan"),
        (f" {stats['resource_usage']['memory_percent']:.0f}%", "bright_green"),
        ("  ┃  Net:", "cyan"),
        (f" {stats['resource_usage']['network_mb']:.1f}MB", "bold white"),
    )
    lines = [status] + [Text(line, style="bold bright_green") for line in logs[-30:]]
    return Panel(
        Group(*lines),
        title="🦾 Verbose Output",
        border_style="bright_cyan",
        box=DOUBLE,
        padding=(1, 2),
    )


class NightOwlDashboard:
    """
    Top-level dashboard class responsible for:
    - Setting up Rich Layout
    - Refreshing panels on a timer
    - Updating layout with orchestrator output
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.layout = Layout()
        self.refresh_rate = 2  # seconds
        self._setup_layout()

    def _setup_layout(self):
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=6),
        )

        self.layout["main"].split_row(
            Layout(name="center", ratio=2),
            Layout(name="right", size=48),
        )

        self.layout["right"].split_column(
            Layout(name="tools", ratio=2),
            Layout(name="results", ratio=2),
            Layout(name="errors", size=8),
        )

    async def run(self):
        start_time = datetime.now()
        with Live(self.layout, refresh_per_second=1 / self.refresh_rate):
            task = asyncio.create_task(self.orchestrator.run())
            while not task.done():
                self.update_dashboard(start=start_time, now=datetime.now())
                await asyncio.sleep(self.refresh_rate)
            self.update_dashboard(start=start_time, now=datetime.now())
            await asyncio.sleep(2)

    def update_dashboard(self, start, now):
        stats = self.orchestrator.get_scan_statistics()

        # Header Panel
        self.layout["header"].update(
            create_header_panel(
                status="Running",
                start=start,
                now=now,
            )
        )

        # Center Verbose Panel
        self.layout["center"].update(
            create_verbose_panel(
                self.orchestrator.verbose_logs,
                stats,
            )
        )

        # Tools Panel
        self.layout["right"]["tools"].update(
            create_tool_status_panel(self.orchestrator.scan_results)
        )

        # Results Panel
        self.layout["right"]["results"].update(
            create_results_panel(
                self.orchestrator.scan_results,
                getattr(self.orchestrator, "tool_stats", {}),
            )
        )

        # Errors Panel
        self.layout["right"]["errors"].update(
            create_error_panel(
                self.orchestrator.failed_tools,
                self.orchestrator.scan_results,
            )
        )

        # Footer Panel
        self.layout["footer"].update(
            create_footer_panel(stats)
        )
