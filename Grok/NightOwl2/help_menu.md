# NightOwl Help Menu

## Commands
- `python core/main.py -t <target> -m <mode> [-c <tools>] [--resume]`
  - `-t`: Target domain or file with list of domains (e.g., example.com, domains.txt).
  - `-m`: Scan mode (light, deep, deepest, custom).
  - `-c`: Comma-separated list of tools for custom mode (e.g., sublist3r,amass).
  - `--resume`: Resume from last state.

## Scan Modes
- **Light**: Quick scan with Sublist3r, Subfinder, crt.sh.
- **Deep**: All subdomain tools, secret finders, and basic vulnerability scans.
- **Deepest**: Iterative sub-subdomain enumeration, extended OSINT, comprehensive vulnerability scans.
- **Custom**: Select specific tools.

## Output Structure
- Subdomains: `output/subdomains/` (tool-specific outputs, `final_subdomains.txt`, `alive.txt`, `dead.txt`)
- Secrets: `output/important/secret/` (`secrets.txt`)
- Important Domains: `output/important/important.txt`
- Endpoints: `output/important/endpoints/` (`endpoints.txt`)
- Vulnerabilities: `output/vulnerabilities/` (`vuln_*.txt`)
- Reports: `output/reports/` (`<target>_report.html`)
- Errors: `output/errors/errors.log`