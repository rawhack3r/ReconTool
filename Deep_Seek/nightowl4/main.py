#!/usr/bin/env python3
"""
NightOwl Reconnaissance Tool - Enterprise Edition
"""
import argparse
import os
import sys
import asyncio
import signal
import time
from datetime import datetime
from core.dashboard import NightOwlDashboard
from core.orchestrator import NightOwlOrchestrator

def print_banner():
    banner = """
    \033[1;35m
    ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗ ██████╗ ██╗    ██╗██╗
    ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝██╔═══██╗██║    ██║██║
    ██╔██╗ ██║██║██║  ███╗███████║   ██║   ██║   ██║██║ █╗ ██║██║
    ██║╚██╗██║██║██║   ██║██╔══██║   ██║   ██║   ██║██║███╗██║██║
    ██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║
    ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝
    
    \033[1;34mVersion: 4.0 | By: NightOwl Team\033[0m
    \033[0;36mAdvanced Attack Surface Discovery Platform\033[0m
    """
    print(banner)

def handle_interrupt(sig, frame):
    print("\n\033[93m[!] Scan interrupted! Use --resume to continue later\033[0m")
    sys.exit(0)

def main():
    print_banner()
    signal.signal(signal.SIGINT, handle_interrupt)
    
    parser = argparse.ArgumentParser(description="NightOwl - Ultimate Reconnaissance Suite")
    parser.add_argument("target", nargs="?", help="Target domain or file containing targets")
    parser.add_argument("-m", "--mode", choices=["light", "deep", "deeper", "custom"], 
                        default="light", help="Scan depth level")
    parser.add_argument("-t", "--target-type", choices=["single", "list", "wildcard"], 
                        default="single", help="Type of target input")
    parser.add_argument("-c", "--custom-tools", nargs='+', default=[],
                        help="List of tools to run (for custom mode)")
    parser.add_argument("-r", "--resume", action="store_true", 
                        help="Resume from last saved state")
    parser.add_argument("-o", "--output", default="nightowl_report", 
                        help="Output report filename")
    parser.add_argument("--clear", action="store_true", 
                        help="Clear previous state before starting")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed tool output in dashboard")
    parser.add_argument("--distributed", action="store_true",
                        help="Enable distributed scanning mode")
    
    args = parser.parse_args()
    
    if not args.target:
        print("Error: Target is required")
        parser.print_help()
        sys.exit(1)
    
    output_dir = f"outputs/{args.target}"
    os.makedirs(output_dir, exist_ok=True)
    
    dashboard = NightOwlDashboard(verbose=args.verbose)
    dashboard.start()
    dashboard.set_target_info(args.target, args.mode, args.target_type)
    
    orchestrator = NightOwlOrchestrator(
        target=args.target,
        mode=args.mode,
        target_type=args.target_type,
        custom_tools=args.custom_tools,
        output_dir=output_dir,
        dashboard=dashboard,
        resume=args.resume,
        verbose=args.verbose,
        distributed=args.distributed
    )
    
    try:
        asyncio.run(orchestrator.execute_workflow())
        dashboard.show_success(f"Recon completed! Report saved to {output_dir}/reports/{args.output}.html")
    except Exception as e:
        dashboard.show_error(f"Critical error: {str(e)}")
    finally:
        dashboard.stop()

if __name__ == "__main__":
    main()