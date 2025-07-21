import argparse
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.stealth import StealthManager
import validators
import shlex

# Add these imports at the TOP
from typing import Set, List, Dict, Any
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn
import subprocess
import json
import sys
import psutil
import shutil
from utils.subdomain import SubdomainScanner
from utils.active_scan import ActiveScanner
from utils.vuln_scan import VulnScanner
from utils.reporting import ReportGenerator

console = Console()

class ReconTool:
    def __init__(self, targets: str, mode: str = "default"):
        self.targets = self._validate_targets(targets.split(','))
        self.mode = mode
        self.proxies = self._load_proxies()
        self.results: Dict[str, Any] = {
            "subdomains": set(),
            "vulns": [],
            "live_domains": [],
            "errors": []
        }
        self._validate_dependencies()

    # ... rest of code ...

    def _validate_targets(self, targets: List[str]) -> List[str]:
        return [t for t in targets if validators.domain(t) or validators.ip_address(t)]

    def _load_proxies(self) -> List[str]:
        return [p.strip() for p in open("proxies.txt", "r").readlines() if p.strip()] if os.path.exists("proxies.txt") else []

    def _validate_dependencies(self):
        required = ["subfinder", "amass", "nuclei", "masscan", "httprobe"]
        missing = [t for t in required if not shutil.which(t)]
        if missing:
            console.print(f"[red]FATAL: Missing tools: {', '.join(missing)}")
            sys.exit(1)

    def run(self):
        with Progress(
            "[cyan]Phase", BarColumn(), "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task("[cyan]Full Recon...", total=4)

            # Phase 1: Subdomains
            progress.update(task, description="[cyan]Phase 1: Subdomains")
            self._run_subdomains()
            progress.advance(task)

            # Phase 2: Active Scan
            progress.update(task, description="[cyan]Phase 2: Active Scan")
            self._run_active_scan()
            progress.advance(task)

            # Phase 3: Vulnerabilities
            progress.update(task, description="[cyan]Phase 3: Vulns")
            self._run_vuln_scan()
            progress.advance(task)

            # Phase 4: Reporting
            progress.update(task, description="[cyan]Phase 4: Reporting")
            self._generate_report()
            progress.advance(task)

    def _run_subdomains(self):
        commands = [
            ("subfinder", "subfinder -dL {targets} -silent -oJ -".format(targets=",".join(self.targets))),
            ("amass", "amass enum -d {targets} -passive -oJ -".format(targets=",".join(self.targets))),
            ("findomain", "findomain -t {targets} -q -oJ -".format(targets=",".join(self.targets)))
        ]
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(self._run_command, cmd) for _, cmd in commands]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results["subdomains"].update(result)
                except Exception as e:
                    self.results["errors"].append(f"{cmd} failed: {str(e)}")

    def _run_command(self, cmd: str) -> List[str]:
        try:
            result = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return json.loads(result.stdout).get("subdomains", [])
        except Exception as e:
            return []

    def _run_active_scan(self):
        scanner = ActiveScanner(self.results["subdomains"], self.proxies)
        scanner.run()
        self.results["live_domains"] = scanner.lived_domains

    def _run_vuln_scan(self):
        scanner = VulnScanner(self.results["live_domains"])
        scanner.run()
        self.results["vulns"] = scanner.findings

    def _generate_report(self):
        report_gen = ReportGenerator()
        report_gen.generate_report(
            subdomains=self.results["subdomains"],
            vulns=self.results["vulns"],
            live_domains=self.results["live_domains"]
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced Recon Tool")
    parser.add_argument("--targets", required=True, help="Domain/IP list (comma-separated)")
    parser.add_argument("--mode", default="default", choices=["default", "deep"], help="Scan mode")
    args = parser.parse_args()
    
    try:
        tool = ReconTool(args.targets, args.mode)
        tool.run()
    except Exception as e:
        console.print(f"[red]FATAL ERROR: {str(e)}")
        sys.exit(1)