# NightOwl v3 – Elite Recon & OSINT Framework

![NightOwl Banner](https://your.logo.url/here.png)

## Overview

NightOwl v3 is a powerful, modular reconnaissance automation platform designed for comprehensive subdomain discovery, secret and asset extraction, endpoint mapping, and vulnerability assessment with OWASP Top 10 awareness. It features a real-time interactive CLI UI, resume and error recovery, and rich HTML/Markdown report generation.

## Features

- Multi-tool subdomain enumeration including Subfinder, Amass, Assetfinder, Findomain, CRT.sh, Sublist3r
- Secret, email, name, phone number extraction with organized output folders
- Phase driven scans: Light | Deep | Custom mode selection
- OWASP Top 10 detection via Nuclei templates
- Real-time resource monitoring & beautiful CLI interface powered by Rich
- Resume interrupted scans
- Auto-generated Markdown and HTML scan reports with visual icons
- Docker ready containerized installer via `installer.sh`

## Quick Start

1. Run installer to prepare environment:
    ```
    bash installer.sh
    ```
2. Run recon scan:
    ```
    python3 core/main.py --target example.com --mode deep
    ```
3. Resume interrupted scan:
    ```
    python3 core/main.py --resume --target example.com
    ```
4. View reports:
    - `outputs/example.com/report.md`
    - `outputs/example.com/report.html`

## Extending & Customizing

- Add or edit tools in `configs/tools.yaml`
- Customize scan phases and tools in `configs/scan_profiles.yaml`
- Add plugins to `plugins/` folder
- Modify OWASP templates in `data/owasp_top10_templates.yaml`

## Contributing

Feel free to submit issues or PRs on the [GitHub repo](https://github.com/youruser/nightowl).

## License

MIT License — see LICENSE file.
