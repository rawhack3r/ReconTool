#!/usr/bin/env python3
"""
ReconX - Advanced Bug Bounty Reconnaissance Tool
"""
import os
import sys
import argparse
from rich.console import Console
from core.scanner import ReconScanner
from core.progress import display_banner

console = Console()

def main():
    display_banner()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='ReconX - Advanced Bug Bounty Reconnaissance Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-t', '--target', help='Single target domain')
    parser.add_argument('-l', '--list', help='File containing list of targets')
    parser.add_argument('-m', '--mode', choices=['default', 'deep'], default='default', 
                        help='Scanning mode')
    parser.add_argument('-o', '--output', default='./reconx_results', 
                        help='Output directory')
    parser.add_argument('-c', '--concurrency', type=int, default=10,
                        help='Number of concurrent workers')
    parser.add_argument('--max-resources', action='store_true',
                        help='Enable resource usage limits')
    parser.add_argument('--install-deps', action='store_true',
                        help='Install required dependencies')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize scanner
    scanner = ReconScanner(
        target=args.target,
        target_list=args.list,
        mode=args.mode,
        output_dir=args.output,
        concurrency=args.concurrency,
        max_resources=args.max_resources
    )
    
    try:
        if scanner.run():
            report_path = scanner.generate_report()
            if report_path:
                console.print(f"\n[bold green]✓ Scan completed successfully![/bold green]")
                console.print(f"[bold]📊 Report generated:[/bold] [cyan]{report_path}[/cyan]")
            else:
                console.print("\n[red]⚠️ Scan completed with report generation errors[/red]")
        else:
            console.print("\n[red]⚠️ Scan failed to complete[/red]")
    except KeyboardInterrupt:
        console.print("\n[!] Scan interrupted by user")
    except Exception as e:
        console.print(f"\n[red][!] Critical error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()