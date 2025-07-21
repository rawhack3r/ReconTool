Advanced Recon Tool v2.5 - Bug Bounty Edition
A comprehensive reconnaissance tool for bug bounty hunting, combining methodologies from NahamSec, Jason Haddix, ReconFTW, BBOT, and OneForAll. Designed for private use and VPS deployment (Linux/ARM).
Features

Subdomain Enumeration: Passive (subfinder, amass, crtsh, sublist3r, waybackurls, dnsdumpster) and active (amass_active, ffuf) with recursive enumeration (Deep mode).
GitHub Recon: Searches for sensitive data (API keys, passwords, .env) using GitHub dorks.
Port Scanning: Fast scanning (naabu), detailed service enumeration (nmap).
Web Scanning: Vulnerability scanning (nuclei), directory fuzzing (ffuf), parameter discovery (paramspider).
OSINT: Email/domain harvesting (theHarvester), metadata extraction (metagoofil).
Visual Recon: Screenshots (gowitness).
Modes: Default (quick, low resource) and Deep (comprehensive).
Error Handling: Skips failed tools, logs errors, suggests retries.
UI: Futuristic console with checklist, progress (10%-100%), CPU/RAM usage.
Output: HTML report with subdomains, vulnerabilities, GitHub findings, screenshots.

Setup

Prerequisites:sudo apt-get install -y python3 python3-pip golang jq curl


Directory Structure:recon-tool/
├── config.json
├── dnsdumpster.py
├── recon_tool.py
├── requirements.txt
├── README.md
├── templates/
│   └── README.md
└── wordlists/
    ├── subdomains-top1million-5000.txt
    ├── raft-medium-directories.txt
    ├── raft-large-directories.txt


Install Dependencies:pip3 install -r requirements.txt
nuclei -update-templates
mv ~/nuclei-templates templates/


Wordlists (recommended):git clone https://github.com/danielmiessler/SecLists.git
cp SecLists/Discovery/DNS/subdomains-top1million-5000.txt wordlists/
cp SecLists/Discovery/Web-Content/raft-medium-directories.txt wordlists/
cp SecLists/Discovery/Web-Content/raft-large-directories.txt wordlists/
rm -rf SecLists


API Keys:
Configure subfinder (~/.config/subfinder/config.yaml) and findomain with API keys (VirusTotal, PassiveTotal).



Usage
python3 recon_tool.py --target example.com --output ~/recon/test --mode default
python3 recon_tool.py --target example.com --output ~/recon/test --mode deep
python3 recon_tool.py --list targets.txt --mode default
python3 recon_tool.py --wildcard *.example.com --mode deep


--cpu-limit 50: Limit CPU usage.
--timeout 600: Timeout per command (seconds).
Output: ~/recon/test/example_com/ with subdomains, ports, vulnerabilities, screenshots, report.html.

Notes

Legal: Use only on in-scope bug bounty targets.
DNSDumpster: Requires dnsdumpster.py. Replace with API key for better results.
Performance: Deep mode is resource-intensive; use on VPS with 4GB+ RAM.
ARM Support: Compatible with ARM (e.g., Raspberry Pi).

Checklist

 Verify Linux environment (Python 3.8+, Go, jq, curl).
 Set up directory structure.
 Install dependencies.
 Configure API keys.
 Run Default mode.
 Run Deep mode.
 Review results (report.html, errors.log).
 Retry failed tools (errors.log).
