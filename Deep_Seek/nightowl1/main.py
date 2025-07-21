#!/usr/bin/env python3
"""
NightOwl Reconnaissance Tool - by n00bhack3r
Made with the help of DeepSeek
"""

import argparse
import sys
from core.orchestrator import NightOwlOrchestrator
from ui.dashboard import NightOwlDashboard
from core.state_manager import save_state, load_state, clear_state
from core.error_handler import ErrorHandler
from ui.web_ui import start_web_interface
from config.settings import VERSION, AUTHOR, SCAN_MODES

def print_banner():
    banner = f"""
    \033[1;35m
     _   _ _       _   _          ___          _ 
    | \ | (_) __ _| |_| |_ ___   / _ \ _ __ __| |
    |  \| | |/ _` | __| __/ _ \ | | | | '__/ _` |
    | |\  | | (_| | |_| ||  __/ | |_| | | | (_| |
    |_| \_|_|\__, |\__|\__\___|  \___/|_|  \__,_|
              |___/                              
    
    \033[1;34mVersion: {VERSION} | By: {AUTHOR}\033[0m
    """
    print(banner)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="NightOwl - Advanced Reconnaissance Suite")
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
    parser.add_argument("-w", "--web-ui", action="store_true", 
                        help="Enable web-based interface")
    parser.add_argument("--clear", action="store_true", 
                        help="Clear previous state before starting")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_state()
        print("\033[92m[✓] Previous state cleared\033[0m")
    
    # Initialize dashboard
    dashboard = NightOwlDashboard()
    
    # Initialize orchestrator
    orchestrator = NightOwlOrchestrator(
        target=args.target,
        mode=args.mode,
        target_type=args.target_type,
        custom_tools=args.custom_tools,
        dashboard=dashboard,
        resume=args.resume
    )
    
    try:
        if args.web_ui:
            start_web_interface(orchestrator)
        else:
            orchestrator.execute_workflow()
            report_path = orchestrator.generate_report(args.output)
            dashboard.show_success(f"Recon completed! Report saved to {report_path}")
            
    except KeyboardInterrupt:
        save_state(orchestrator.get_current_state())
        dashboard.show_warning("\n🛑 Scan interrupted. State saved for resumption.")
    except Exception as e:
        save_state(orchestrator.get_current_state())
        ErrorHandler.log_critical(str(e), args.target)
        dashboard.show_error(f"🔥 Critical error: {str(e)}\nState saved for debugging.")

if __name__ == "__main__":
    main()