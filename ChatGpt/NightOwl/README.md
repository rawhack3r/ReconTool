# NightOwl Recon Framework
_By n00bhack3r with ChatGPT_

NightOwl is a modular, high‑coverage, low‑waste bug bounty reconnaissance automation framework designed to:
- Enumerate subdomains (passive/active/brute)
- Probe for live hosts, services, tech
- Extract emails, secrets, sensitive paths
- Gather OSINT & historical endpoints
- Scan for takeovers & vulnerabilities
- Produce actionable HTML & Markdown reports
- Resume scans, re-run failed tools, run light/deep/custom profiles

---

## Quick Start
git clone <your repo>
cd NightOwl
pip install -r requirements.txt
python3 main.py --target example.com --scan-level light

## Scan Levels
- **light**: Fast, low resource, passive + probe + critical vuln
- **deep**: All phases (active, brute, OSINT, vuln full, secrets)
- **custom**: User selects tools/phases via CLI

---

## Output Layout
See docs in `help_menu.md`.

---

## Credits
Inspired by: BBOT, reconFTW, rs0n, Nahamsec, Jhaddix, ArmSec, UncleRat, and community writeups.

