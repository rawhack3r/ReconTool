#!/usr/bin/env python3
"""
ReconMaster Ultra - Main Entry Point
Version: 3.0
"""

import argparse
import logging
from core import ReconScanner, load_config, setup_logging

def main():
    parser = argparse.ArgumentParser(description="ReconMaster Ultra - Advanced Reconnaissance Tool")
    parser.add_argument("target", help="Target domain or file containing targets")
    parser.add_argument("-o", "--output", default="recon_results", help="Output directory")
    parser.add_argument("-m", "--mode", choices=["lightning", "default", "deep", "assassin"], 
                        default="default", help="Scanning mode")
    parser.add_argument("-w", "--wildcard", action="store_true", help="Handle wildcard domains")
    parser.add_argument("--ai", action="store_true", help="Enable AI-powered analysis")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(debug=args.debug)
    
    # Initialize scanner
    scanner = ReconScanner(
        target=args.target,
        output_dir=args.output,
        mode=args.mode,
        wildcard=args.wildcard,
        ai_enabled=args.ai,
        config=config
    )
    
    # Execute scan
    scanner.run_scan()

if __name__ == "__main__":
    main()