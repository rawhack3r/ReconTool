#!/usr/bin/env python3

import sys
import asyncio
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from core.orchestrator import NightOwlOrchestrator
from ui.dashboard import NightOwlDashboard
from config.settings import WORKFLOW_PHASES

console = Console()

class NightOwlCLI:
    def __init__(self):
        self.orchestrator = None

    def parse_args(self):
        parser = argparse.ArgumentParser(description="NightOwl Recon")
        parser.add_argument("-t", "--target", required=True, help="Target domain or file")
        parser.add_argument("-m", "--mode", choices=["light", "deep"], default="light", help="Scan mode")
        parser.add_argument("-o", "--output", default="output", help="Output directory")
        parser.add_argument("--no-ui", action="store_true", help="Disable interactive UI")
        return parser.parse_args()

    async def run(self):
        args = self.parse_args()
        Path(args.output).mkdir(parents=True, exist_ok=True)
        self.orchestrator = NightOwlOrchestrator(
            target=args.target,
            mode=args.mode,
            output_dir=args.output,
        )
        if args.no_ui:
            await self.orchestrator.run()
        else:
            await NightOwlDashboard(self.orchestrator).run()

def main():
    asyncio.run(NightOwlCLI().run())

if __name__ == "__main__":
    main()
