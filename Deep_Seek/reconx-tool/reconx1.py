#!/usr/bin/env python3
"""
ReconX - Advanced Bug Bounty Reconnaissance Tool
"""
import argparse
import os
import sys
from core.scanner import ReconScanner
from core.progress import display_banner
from core.utils import check_dependencies, setup_environment

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
    parser.add_argument('-o', '--output', default='./outputs', 
                        help='Output directory')
    parser.add_argument('-c', '--concurrency', type=int, default=10,
                        help='Number of concurrent workers')
    parser.add_argument('--max-resources', action='store_true',
                        help='Enable resource usage limits')
    parser.add_argument('--install-deps', action='store_true',
                        help='Install required dependencies')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if args.install_deps:
        check_dependencies(install_missing=True)
    
    # Validate targets
    if not args.target and not args.list:
        print("Error: You must specify either --target or --list")
        sys.exit(1)
    
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
        scanner.run()
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user")
    except Exception as e:
        print(f"\n[!] Critical error: {str(e)}")
    finally:
        scanner.generate_report()

if __name__ == '__main__':
    main()