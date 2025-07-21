#!/usr/bin/env python3
"""
NightOwl Reconnaissance Tool - Ultimate Edition
"""
import argparse
import os
import sys
import asyncio
import signal
from datetime import datetime

from core.dashboard import NightOwlDashboard
from core.orchestrator import NightOwlOrchestrator
from core.state_manager import StateManager
from core.error_handler import ErrorHandler

def print_banner():
    banner = f"""
    \033[1;35m
    ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗ ██████╗ ██╗    ██╗██╗
    ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝██╔═══██╗██║    ██║██║
    ██╔██╗ ██║██║██║  ███╗███████║   ██║   ██║   ██║██║ █╗ ██║██║
    ██║╚██╗██║██║██║   ██║██╔══██║   ██║   ██║   ██║██║███╗██║██║
    ██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║
    ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝
    
    \033[1;34mVersion: 3.0 | By: NightOwl Team\033[0m
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
    parser.add_argument("target", help="Target domain or file containing targets")
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
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = f"outputs/{args.target}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize dashboard
    dashboard = NightOwlDashboard(verbose=args.verbose)
    dashboard.start()
    dashboard.set_target_info(args.target, args.mode, args.target_type)
    
    # Initialize orchestrator
    orchestrator = NightOwlOrchestrator(
        target=args.target,
        mode=args.mode,
        target_type=args.target_type,
        custom_tools=args.custom_tools,
        output_dir=output_dir,
        dashboard=dashboard,
        resume=args.resume,
        verbose=args.verbose
    )
    
    try:
        asyncio.run(orchestrator.execute_workflow())
        dashboard.show_success(f"Recon completed! Report saved to {output_dir}/reports/{args.output}.html")
    except Exception as e:
        dashboard.show_error(f"Critical error: {str(e)}")
        ErrorHandler().log_critical(f"Main execution failed: {str(e)}", args.target)
    finally:
        dashboard.stop()

if __name__ == "__main__":
    main()