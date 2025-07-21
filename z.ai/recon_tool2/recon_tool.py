import argparse
import os
import subprocess
import json
import sys
import psutil
from typing import Set, List, Dict
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.subdomain import SubdomainScanner
from utils.active_scan import ActiveScanner
from utils.vuln_scan import VulnScanner
from utils.reporting import ReportGenerator
from utils.stealth import StealthManager
import validators
import shutil

console = Console()

class ReconTool:
    def __init__(self, targets: str, mode: str = "default"):
        self.targets = self._validate_targets(targets.split(','))
        self.mode = mode
        self.proxies = self._load_proxies()
        self.results = {
            "subdomains": set(),
            "vulns": [],
            "live_domains": [],
            "errors": []
        }
        self._validate_dependencies()

    def _validate_targets(self, targets: List[str]) -> List[str]:
        return [t for t in targets if validators.domain(t) or validators.ipv4(t) or validators.ipv6(t)]

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
            ("subfinder", self._run_subfinder),
            ("amass", self._run_amass),
            ("findomain", self._run_findomain)
        ]
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fn) for _, fn in commands]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    self.results["subdomains"].update(result)
                except Exception as e:
                    self.results["errors"].append(f"{cmd} failed: {str(e)}")

    def _run_subfinder(self) -> List[str]:
        return self._run_command("subfinder -dL {targets} -silent -oJ -".format(targets=",".join(self.targets)))

    def _run_amass(self) -> List[str]:
        return self._run_command("amass enum -d {targets} -passive -oJ -".format(targets=",".join(self.targets)))

    def _run_command(self, cmd: str) -> List[str]:
        try:
            process = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=120,
                env={"HTTP_PROXY": random.choice(self.proxies)} if self.proxies else {}
            )
            return json.loads(process.stdout).get("subdomains", [])
        except Exception as e:
            return []