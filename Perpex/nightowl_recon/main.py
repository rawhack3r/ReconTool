#!/usr/bin/env python3
"""
NightOwl Enhanced Reconnaissance Suite
Version: 2.1.0
Author: n00bhack3r
"""

import sys
import asyncio
import argparse
import signal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from core.orchestrator import NightOwlOrchestrator
from ui.dashboard import NightOwlDashboard
from config.settings import BANNER, VERSION, AUTHOR, TOOL_CATEGORIES
from utils.helpers import validate_target, setup_directories
from utils.dependency_checker import check_dependencies

console = Console()


class NightOwlCLI:
    def __init__(self):
        self.orchestrator = None

    def setup_signals(self):
        def handler(sig, frame):
            console.print("\n[yellow]Interrupt received. Saving state and exiting...[/yellow]")
            if self.orchestrator:
                self.orchestrator.save_state()
            sys.exit(0)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def display_banner(self):
        console.print(Panel(f"{BANNER}\nVersion: {VERSION} | Author: {AUTHOR}",
                            title="NightOwl Recon", border_style="cyan"))

    def parse_args(self):
        parser = argparse.ArgumentParser(description="NightOwl Recon")
        parser.add_argument("-t", "--target", required=True, help="Target domain or file")
        parser.add_argument("-m", "--mode", choices=["light", "deep", "custom"], default="deep", help="Scan mode")
        parser.add_argument("-o", "--output", default="output", help="Output directory")
        parser.add_argument("--resume", action="store_true", help="Resume previous scan")
        parser.add_argument("--config", help="Custom config file")
        parser.add_argument("--tools", nargs="+", help="Custom tools (with --mode custom)")
        parser.add_argument("--no-ui", action="store_true", help="Disable interactive UI")
        parser.add_argument("--timeout", type=int, default=300, help="Per-tool timeout (seconds)")
        parser.add_argument("--rate-limit", type=int, default=10, help="Requests per second limit")
        parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
        parser.add_argument("--help-menu", action="store_true", help="Show detailed help")
        parser.add_argument("--list-tools", action="store_true", help="List available tools")
        parser.add_argument("--check-deps", action="store_true", help="Check binary dependencies")
        return parser.parse_args()

    async def run(self):
        self.setup_signals()
        self.display_banner()

        args = self.parse_args()

        if args.help_menu:
            console.print(Path("help_menu.md").read_text())
            return

        if args.list_tools:
            for cat, tools in TOOL_CATEGORIES.items():
                console.print(f"[bold green]{cat}:[/bold green] {', '.join(tools)}")
            return

        if args.check_deps:
            deps = check_dependencies()
            for tool, stat in deps.items():
                if stat["available"]:
                    console.print(f"[green]✓ {tool}[/green] — {stat['version']}")
                else:
                    console.print(f"[red]✗ {tool}[/red] — {stat['error']}")
            return

        if not validate_target(args.target):
            console.print(f"[red]Invalid target: {args.target}[/red]")
            return

        setup_directories(args.output)

        console.print(Panel(
            f"[bold]Target:[/bold] {args.target}\n"
            f"[bold]Mode:[/bold] {args.mode}\n"
            f"[bold]Output:[/bold] {args.output}\n"
            f"[bold]Timeout:[/bold] {args.timeout}s\n"
            f"[bold]Rate Limit:[/bold] {args.rate_limit}/s\n"
            f"[bold]Custom Tools:[/bold] {', '.join(args.tools) if args.tools else 'Default'}",
            title="Scan Configuration", border_style="yellow"
        ))

        if not args.no_ui:
            if not Confirm.ask("Start scan?", default=True):
                console.print("[yellow]Scan cancelled by user[/yellow]")
                return

        self.orchestrator = NightOwlOrchestrator(
            target=args.target,
            mode=args.mode,
            output_dir=args.output,
            timeout=args.timeout,
            rate_limit=args.rate_limit,
            resume=args.resume,
            custom_tools=args.tools,
            config_file=args.config,
            verbose=args.verbose
        )

        if args.no_ui:
            await self.orchestrator.run()
        else:
            await NightOwlDashboard(self.orchestrator).run()


def main():
    asyncio.run(NightOwlCLI().run())


if __name__ == "__main__":
    main()
