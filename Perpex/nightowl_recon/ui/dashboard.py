import asyncio
from datetime import datetime
from rich.live import Live
from rich.layout import Layout
from .components import (
    create_header_panel, create_resource_panel, create_target_panel,
    create_phase_panel, create_tool_status_panel, create_results_panel,
    create_error_panel, create_summary_panel
)

class NightOwlDashboard:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.layout = Layout()
        self.refresh_rate = 2
        self._setup_layout()

    def _setup_layout(self):
        self.layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        self.layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right", size=28)
        )
        self.layout["left"].split_column(
            Layout(name="target", size=3),
            Layout(name="resources", size=3),
            Layout(name="tools"),
            Layout(name="results")
        )
        self.layout["right"].split_column(
            Layout(name="phases"),
            Layout(name="errors", size=8)
        )

    async def run(self):
        now = datetime.now()
        with Live(self.layout, refresh_per_second=1/self.refresh_rate) as live:
            orchestrator_task = asyncio.create_task(self.orchestrator.run())
            while not orchestrator_task.done():
                self.update_dashboard(now, datetime.now())
                await asyncio.sleep(self.refresh_rate)
            self.update_dashboard(now, datetime.now())
            await asyncio.sleep(2)

    def update_dashboard(self, start_time, current_time):
        stats = self.orchestrator.get_scan_statistics()
        self.layout["header"].update(create_header_panel(
            status="Running", start_time=start_time, current_time=current_time
        ))
        self.layout["left"]["target"].update(
            create_target_panel(stats['target'], stats['mode'], stats['overall_progress'])
        )
        self.layout["left"]["resources"].update(create_resource_panel(stats['resource_usage']))
        self.layout["right"]["phases"].update(
            create_phase_panel(stats['current_phase'], stats['total_phases'], None)
        )
        self.layout["left"]["tools"].update(create_tool_status_panel(self.orchestrator.scan_results))
        self.layout["left"]["results"].update(create_results_panel(self.orchestrator.scan_results))
        self.layout["right"]["errors"].update(create_error_panel(
            self.orchestrator.get_failed_tools(), self.orchestrator.scan_results
        ))
        self.layout["footer"].update(create_summary_panel(stats))
