```markdown
# NightOwl Reconnaissance Tool

NightOwl is a state-of-the-art reconnaissance automation tool designed for penetration testers and bug bounty hunters. It integrates multiple tools for subdomain enumeration, secret finding, asset identification, endpoint extraction, and vulnerability scanning, with a real-time terminal and web-based UI, robust error handling, and comprehensive HTML reports.

## Features
- **Subdomain Enumeration**: Integrates Sublist3r, Amass, Assetfinder, Findomain, Subfinder, dnsx, Gotator, puredns, crt.sh, subbrute.
- **Scan Modes**: Light, Deep, Deepest, Custom.
- **Real-Time UI**: Terminal dashboard with resource usage, target details, and workflow progress; Flask-based web dashboard.
- **Error Handling**: Logs errors, skips failed tools, supports re-launching, and resumes scans.
- **Output**: Text files for tool outputs, merged results, alive/dead domains, important findings, and HTML reports.
- **Vulnerability Scanning**: OWASP Top 10 checks with Nuclei and ZAP, ML-based false-positive reduction.
- **OSINT**: Extracts emails, usernames, mobile numbers using hunter.io and github_scanner.
- **Performance**: Parallel execution, resource monitoring, and optimization for low CPU/RAM usage.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/nightowl/nightowl.git
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install external tools (e.g., sublist3r, amass, nuclei, httpx, subjack, etc.) and configure API keys in `config/config.yaml`.

## Usage
```bash
python core/main.py -t example.com -m deep
```
- `-t`: Target domain or file with list of domains.
- `-m`: Scan mode (light, deep, deepest, custom).
- `-c`: Comma-separated list of tools for custom mode.
- `--resume`: Resume from last state.

## Output Structure
- Subdomains: `output/subdomains/final_subdomains.txt`, `alive.txt`, `dead.txt`
- Secrets: `output/important/secret/secrets.txt`
- Important Domains: `output/important/important.txt`
- Endpoints: `output/important/endpoints/endpoints.txt`
- Vulnerabilities: `output/vulnerabilities/vuln_*.txt`
- Reports: `output/reports/<target>_report.html`
- Errors: `output/errors/errors.log`

## Manual Check Methodology
For sensitive domains (e.g., admin, login, dev):
1. **Authentication Testing**: Check for weak credentials, misconfigured SSO, or OAuth flaws using Burp Suite.
2. **Access Control**: Test for unauthorized access to admin panels or APIs, check for IDOR.
3. **Parameter Tampering**: Fuzz parameters for SQLi, XSS, SSRF using Burp Intruder.
4. **API Testing**: Use Postman to test for rate limiting or data leaks.
5. **Historical URLs**: Review waybackurls for outdated or sensitive content.
6. **Subdomain Takeover**: Manually verify subjack results for dangling DNS records.

## Roadmap
1. **Cloud Integration**: Support distributed scanning with Axiom or cloud workers.
2. **AI Enhancements**: Use NLP for subdomain prediction and vulnerability prioritization.
3. **Real-Time Notifications**: Send results to Telegram, Slack, or email.
4. **Plugin System**: Allow custom tool integration via plugins.
5. **Advanced Visualization**: Add interactive charts to the web dashboard.
6. **Containerization**: Package NightOwl in Docker for portability.

## Contributing
Contributions are welcome! Please submit pull requests or open issues on GitHub.
```