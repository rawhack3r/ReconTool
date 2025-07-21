# NightOwl Reconnaissance Tool

NightOwl is an advanced reconnaissance tool designed for offensive security professionals and bug bounty hunters. It automates the reconnaissance process with multiple integrated tools and provides comprehensive reporting.

## Features

- **Subdomain Enumeration**: 12+ tools for comprehensive subdomain discovery
- **Content Discovery**: Directory brute-forcing, JS analysis, and spidering
- **Information Gathering**: Email extraction, secret finding, and PII detection
- **Vulnerability Scanning**: Integrated with Nuclei, ZAP, WPScan, and more
- **Mobile Analysis**: Mobile Security Framework (MobSF) integration
- **Distributed Scanning**: Redis-based task distribution
- **Reporting**: HTML and PDF reports with vulnerability prioritization
- **REST API**: Fully automated scanning workflows

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/nightowl.git
cd nightowl

# Run installation script
chmod +x install.sh
./install.sh

# Activate virtual environment
source .venv/bin/activate



Usage
Basic Scan
bash
python main.py example.com
Deep Scan
bash
python main.py example.com -m deep
Custom Tools
bash
python main.py example.com -m custom -c amass subfinder nuclei
Distributed Scanning
bash
# Start Redis server
redis-server

# Start worker nodes (in separate terminals)
python worker.py
python worker.py

# Run scan with distributed mode
python main.py example.com --distributed

Rest API

# Start API server
python api_server.py

# Start a scan via API
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{"target": "example.com", "mode": "deep"}'

# Get report
curl "http://localhost:8000/scan/scan_20250721120000_abc123/report?type=pdf" --output report.pdf