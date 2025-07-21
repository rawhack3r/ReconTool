# ReconMaster Ultra

Advanced Bug Bounty Reconnaissance Tool

## Features
- Comprehensive subdomain enumeration
- Vulnerability scanning with Nuclei
- Cloud asset discovery
- JavaScript analysis for secrets
- Real-time dashboard
- Multiple scan modes
- Professional reporting

## Installation
```bash
git clone https://github.com/yourusername/reconmaster-ultra.git
cd reconmaster-ultra
chmod +x setup.sh
./setup.sh

# Basic scan
python main.py example.com

# Deep scan with AI
python main.py example.com -m deep --ai

# Scan with custom output
python main.py example.com -o my_scan_results


Scan Modes
lightning: Quick surface scan (5-10 mins)

default: Balanced coverage (30-60 mins)

deep: Comprehensive scan (1-2 hours)

assassin: Full reconnaissance with AI (2-4 hours)

Output Structure
Results are organized in timestamped directories:

subdomains/: Discovered subdomains

services/: Live HTTP services

vulns/: Vulnerability scan results

reports/: HTML, JSON and Markdown reports

screenshots/: Visual reconnaissance