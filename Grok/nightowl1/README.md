NightOwl Reconnaissance Suite
NightOwl is a comprehensive, automated reconnaissance tool for bug bounty hunters, designed to maximize attack surface coverage with minimal resources. It supports subdomain enumeration, secret finding, endpoint extraction, vulnerability scanning, and cloud/IP discovery.
Features

Multi-Tool Integration: Uses subfinder, amass, sublist3r, dnsrecon, gf, nuclei, and more.
Modes: light (basic tools), deep (all tools), custom (user-selected tools).
Real-Time Dashboard: Flask/React-based UI with system resource monitoring, phase checklist, and tool outputs.
Robust Error Handling: Retries, detailed logging, resume functionality.
Output: Per-tool .txt, merged final.txt, live.txt, non_resolved.txt, important.txt, secrets.txt, vulns.txt, and HTML report.
OWASP Top 10: Automated vulnerability scanning with nuclei.

Installation
git clone https://github.com/your-repo/nightowl.git
cd nightowl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo apt install dnsrecon
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/tomnomnom/assetfinder@latest
# Install other tools (see below)

Tool Dependencies
# Subdomain Enumeration
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/tomnomnom/assetfinder@latest
cargo install findomain
go install github.com/OWASP/Amass/v3/...@master
pip install sublist3r
go install github.com/003random/gotator@latest
go install github.com/projectdiscovery/puredns/v2/cmd/puredns@latest
pip install subadub
sudo apt install dnsrecon
go install github.com/SSLMate/certspotter/cmd/certspotter@latest
pip install dnsgen

# Secret Finding
go install github.com/trufflesecurity/trufflehog@latest
go install github.com/gitleaks/gitleaks/v8@latest
git clone https://github.com/m4ll0k/SecretFinder
pip install emailhunter
git clone https://github.com/laramies/theHarvester
go install github.com/tomnomnom/gf@latest
git clone https://github.com/1ndianl33t/Gf-Patterns
cp Gf-Patterns/*.json ~/.gf/

# Endpoint Extraction
go install github.com/projectdiscovery/katana/cmd/katana@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/tomnomnom/waybackurls@latest

# Vulnerability Scanning
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
sudo snap install zaproxy --classic
sudo ln -s /snap/zaproxy/current/zap-api-scan.py /usr/local/bin/zap-api-scan.py
sudo apt install metasploit-framework

# Cloud and IP Discovery
git clone https://github.com/initstring/cloud_enum
pip install dnsdumpster
pip install shodan
export SHODAN_API_KEY=your_api_key
export EMAILHUNTER_API_KEY=your_api_key

# Other
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
pip install flask jinja2 psutil pyyaml

Usage
source venv/bin/activate
python3 main.py --target example.com --mode deep
# Custom mode
python3 main.py --target example.com --mode custom --custom-tools subfinder amass
# Resume interrupted scan
python3 main.py --target example.com --mode deep --resume
# Retry failed tools
python3 main.py --target example.com --mode deep --retry-failed
# Run dashboard
python3 dashboard.py

Outputs

output/<tool>_<target>.txt: Individual tool outputs.
output/final_<target>.txt: Merged results.
output/live_<target>.txt: Live hosts.
output/non_resolved_<target>.txt: Non-resolved hosts.
output/important_<target>.txt: Important assets.
output/secrets_<target>.txt: Secrets, emails, usernames.
output/vulns_<target>.txt: Vulnerabilities.
output/report_<target>.html: HTML report.

Dashboard
Access at http://localhost:5000 after running python3 dashboard.py.
Manual Review Checklist

Sensitive Domains: Check domains with api, admin, test, dev, staging for misconfigurations.
Secrets: Verify API keys, tokens, and credentials in secrets.txt.
Vulnerabilities: Test OWASP Top 10 issues (XSS, SQLi) manually on domains in vulns.txt.
Endpoints: Explore URLs in important.txt for sensitive paths (e.g., /admin, /login).
Assets: Investigate IPs and cloud buckets for exposed services.

Testing
python3 -m unittest tests/test_nightowl.py
pylint *.py core/*.py tools/**/*.py
