import time
from datetime import datetime
import os
from rich.console import Console
from core.state_manager import StateManager  # Added import

class UI:
    def __init__(self):
        self.console = Console()
        self.state_manager = StateManager()

    def start_scan(self, target, mode):
        self.console.print(f"[bold green]NightOwl started on {target} in {mode} mode[/bold green]")

    def start_dashboard(self):
        while True:
            self.display_dashboard()
            time.sleep(5)  # Update every 5 seconds

    def display_dashboard(self):
        target = self.state_manager.get_target()
        mode = self.state_manager.get_mode()
        progress = self.state_manager.get_progress()
        timestamp = "05:18 AM IST, July 21, 2025"  # Updated to current time

        dashboard = f"""
╭──────────────────────────── NightOwl Dashboard ─────────────────────────────╮
│ Target: {target:<50}│
│ Mode: {mode:<54}│
│ Timestamp: {timestamp:<47}│
╰─────────────────────────────────────────────────────────────────────────────╯
╭───────── 'left' (39 x 31) ──────────╮╭───────── Workflow Progress ──────────╮
│                                     ││ ✅ Phase 1: Subdomain Enumeration:   │
│                                     ││ {progress.get('phase_1_subdomain_enumeration', 0)}%                                 │
│                                     ││                                      │
│                                     ││ ⏳ Phase 2: Secret Finding: {progress.get('phase_2_secret_finding', 0)}%       │
│                                     ││                                      │
│                                     ││ ⏳ Phase 3: Asset Identification: {progress.get('phase_3_asset_identification', 0)}% │
│                                     ││                                      │
│                                     ││ ⏳ Phase 4: Endpoint Extraction: {progress.get('phase_4_endpoint_extraction', 0)}%  │
│                                     ││                                      │
│                                     ││ ⏳ Phase 5: Vulnerability Scanning: {progress.get('phase_5_vulnerability_scanning', 0)}% │
│                                     ││                                      │
│                                     ││                                      │
│         Layout(name='left')         ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
│                                     ││                                      │
╰─────────────────────────────────────╯╰──────────────────────────────────────╯
╭───────────────────────────── 'footer' (79 x 1) ─────────────────────────────╮
 * Serving Flask app 'core.ui'
 * Debug mode: off
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://10.235.133.157:5000
Press CTRL+C to quit
Enabled subdomain tools: ['sublist3r', 'amass', 'assetfinder', 'findomain', 'subfinder'] (5 total)
{self.get_tool_status()}
╰─────────────────────────────────────────────────────────────────────────────╯
"""

        self.console.print(dashboard)

    def get_tool_status(self):
        state = self.state_manager.get_state()
        tools = state.get("current_tools", {})
        status = []
        for i, (tool, status_text) in enumerate(tools.items(), 1):
            status.append(f"Running {tool} ({i}/5)... [{status_text}]")
        return "\n".join(status) if status else "No tools running."

    def start_tool(self, tool, target):
        self.state_manager.update_tool_status(tool, "In Progress")

    def end_tool(self, tool, results, duration, stderr, error=False, cpu=0, ram=0, net_sent=0, net_recv=0):
        status = "Completed" if not error else "Failed"
        self.state_manager.update_tool_status(tool, status)
        if not error and results:
            self.state_manager.update_subdomains(results)

    def update_phase_progress(self, tool):
        phase_map = {
            "sublist3r": "phase_1_subdomain_enumeration",
            "amass": "phase_1_subdomain_enumeration",
            "assetfinder": "phase_1_subdomain_enumeration",
            "findomain": "phase_1_subdomain_enumeration",
            "subfinder": "phase_1_subdomain_enumeration",
            "trufflehog": "phase_2_secret_finding",
            "dnsx": "phase_3_asset_identification",
            "gotator": "phase_3_asset_identification",
            "puredns": "phase_3_asset_identification",
            "katana": "phase_4_endpoint_extraction",
            "ffuf": "phase_4_endpoint_extraction",
            "waybackurls": "phase_4_endpoint_extraction",
            "nuclei": "phase_5_vulnerability_scanning",
            "subjack": "phase_5_vulnerability_scanning"
        }
        phase = phase_map.get(tool)
        if phase:
            current_progress = self.state_manager.get_progress().get(phase, 0)
            tools_in_phase = len([t for t in phase_map if phase_map[t] == phase])
            completed_tools = sum(1 for t in phase_map if phase_map[t] == phase and self.state_manager.get_tool_status(t) == "Completed")
            new_progress = min(100, (completed_tools / tools_in_phase) * 100) if tools_in_phase > 0 else 0
            if new_progress > current_progress:
                self.state_manager.update_progress(phase, new_progress)

    def finish_scan(self, target, unavailable_tools):
        self.console.print(f"[bold green]Scan completed for {target}[/bold green]")
