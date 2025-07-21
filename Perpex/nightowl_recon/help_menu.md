# NightOwl Reconnaissance Suite Help

**Usage Examples:**

- Scan a domain in light mode:
  nightowl -t example.com -m light

- Custom scan, choose tools:
  nightowl -t example.com -m custom --tools amass subfinder

- Resume scan:
  nightowl -t example.com --resume

**Output Structure:**
- scans/: Tool outputs in JSON/TXT for each phase.
- reports/: Final HTML, CSV, and JSON reports.
- important/: Aggregated contacts, secrets, key information.

**Manual Testing Suggestions:**
- Review /important for emails, names, directories.
- Follow up on any vulnerabilities flagged in /vulnerabilities.
- Manually verify suspicious or sensitive endpoints.

**See README.md for full documentation.**
