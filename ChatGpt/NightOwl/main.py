#!/usr/bin/env python3
"""
NightOwl Recon - Entry Point
This thin wrapper parses CLI args, builds the ReconTool engine, and runs the scan.
"""
from ui.cli import parse_args
from core.recon_engine import ReconTool
from ui.dashboard import NightOwlUI

def main():
    args = parse_args()
    ui = NightOwlUI()

    ui.show_banner()
    ui.log(f"Target: {args.target}")
    ui.log(f"Scan Level: {args.scan_level}")

    engine = ReconTool(
        target=args.target,
        scan_level=args.scan_level,
        tools=args.tools.split(",") if args.tools else None,
        phases=args.phases.split(",") if args.phases else None,
        resume=args.resume,
        ui=ui,
    )
    engine.run()

if __name__ == "__main__":
    main()
