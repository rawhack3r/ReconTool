#!/usr/bin/env python3
"""
NightOwl Reconnaissance Tool - Futuristic Edition
"""

import argparse
import sys
import traceback
from core.dashboard import NightOwlDashboard
from core.orchestrator import NightOwlOrchestrator
from core.state_manager import clear_state
from core.error_handler import ErrorHandler
from config.settings import VERSION, AUTHOR, SCAN_MODES

def print_banner():
    banner = f"""
    \033[1;35m
    ███╗   ██╗██╗ ██████╗ ██╗  ██╗████████╗ ██████╗ ██╗    ██╗██╗
    ████╗  ██║██║██╔════╝ ██║  ██║╚══██╔══╝██╔═══██╗██║    ██║██║
    ██╔██╗ ██║██║██║  ███╗███████║   ██║   ██║   ██║██║ █╗ ██║██║
    ██║╚██╗██║██║██║   ██║██╔══██║   ██║   ██║   ██║██║███╗██║██║
    ██║ ╚████║██║╚██████╔╝██║  ██║   ██║   ╚██████╔╝╚███╔███╔╝██║
    ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚══╝╚══╝ ╚═╝
    
    \033[1;34mVersion: {VERSION} | By: {AUTHOR}\033[0m
    \033[0;36mAdvanced Attack Surface Discovery Platform\033[0m
    """
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="NightOwl - Futuristic Reconnaissance Suite")
    parser.add_argument("target", help="Target domain or file containing targets")
    parser.add_argument("-m", "--mode", choices=SCAN_MODES, 
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
    
    if args.clear:
        clear_state()
        print("\033[92m[✓] Previous state cleared\033[0m")
    
    # Initialize dashboard
    dashboard = NightOwlDashboard(verbose=args.verbose)
    dashboard.start()
    dashboard.display_header()
    
    # Initialize orchestrator
    orchestrator = NightOwlOrchestrator(
        target=args.target,
        mode=args.mode,
        target_type=args.target_type,
        custom_tools=args.custom_tools,
        dashboard=dashboard,
        resume=args.resume,
        verbose=args.verbose
    )
    
    try:
        orchestrator.execute_workflow()
        report_path = orchestrator.generate_report(args.output)
        dashboard.show_success(f"Recon completed! Report saved to {report_path}")
            
    except KeyboardInterrupt:
        orchestrator.handle_interrupt(signal.SIGINT, None)
    except Exception as e:
        traceback.print_exc()
        ErrorHandler.log_critical(f"Main execution failed: {str(e)}\n{traceback.format_exc()}", args.target)
        dashboard.show_error(f"🔥 Critical error: {str(e)}")
    finally:
        dashboard.stop()

if __name__ == "__main__":
    main()