# NightOwl Reconnaissance Suite

Advanced reconnaissance tool for penetration testers and bug bounty hunters.

## Features
- Multi-mode scanning (light, deep, deeper, custom)
- Comprehensive subdomain enumeration
- Sensitive information extraction (emails, names, credentials)
- OWASP Top 10 vulnerability scanning
- Beautiful terminal and web UI
- Resume interrupted scans
- Customizable workflows

## Installation
```bash
git clone https://github.com/n00bhack3r/nightowl.git
cd nightowl
pip install -r requirements.txt

# Light scan
./main.py example.com -m light

# Deep scan
./main.py example.com -m deep

# Custom scan
./main.py example.com -m custom -c amass nuclei secret_finder

# Resume scan
./main.py example.com -m deep -r

# Web UI mode
./main.py example.com -m deep -w


Scan Modes
Mode	Description
light	Quick subdomain discovery
deep	Comprehensive recon (recommended)
deeper	Full attack surface discovery
custom	Select specific tools to run

outputs/
├── scans/          # Raw tool outputs
├── reports/        # Final HTML/PDF reports
├── important/      # Categorized important findings
│   ├── emails.txt
│   ├── api_keys.txt
│   └── ...
└── vulnerabilities/ # Categorized vulnerabilities
    ├── A1.json     # Injection flaws
    ├── A7.json     # XSS vulnerabilities
    └── ...

    Manual Testing Checklist
After each scan, review outputs/manual_checklist.md for critical areas that require manual testing.

Contribution
Contributions welcome! Please submit PRs with:

New tool integrations

Additional patterns

UI improvements

Performance optimizations


#### 2. Core Functionality (core/)
**__init__.py**
```python
# core/__init__.py
# Package initialization