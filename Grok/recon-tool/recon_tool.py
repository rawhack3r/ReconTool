import os
import json
import subprocess
import time
import psutil
import threading
import argparse
import sys
from datetime import datetime
from pathlib import Path
import re
from multiprocessing import Pool
import shutil
import glob
import requests
from bs4 import BeautifulSoup
import logging
import signal

# ANSI colors for futuristic UI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
RESET = "\033[0m"

class ReconTool:
    def __init__(self, targets, output_dir, mode, config_file="config.json", cpu_limit=80, timeout=600):
        self.targets = targets
        self.mode = mode.lower()
        self.output_dir = Path(output_dir).expanduser()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.error_log = self.output_dir / "errors.log"
        self.checklist = [
            "Subdomain Enumeration", "GitHub Recon", "Port Scanning",
            "Service Enumeration", "Web Scanning", "OSINT", "Visual Reconnaissance"
        ]
        self.checklist_status = ["Pending"] * len(self.checklist)
        self.skipped_tools = []
        self.cpu_limit = cpu_limit
        self.timeout = timeout  # Timeout per command in seconds
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=self.error_log, level=logging.ERROR, format="%(asctime)s %(message)s")
        try:
            with open(config_file) as f:
                self.config = json.load(f)
        except FileNotFoundError:
            print(f"{RED}Error: Config file {config_file} not found{RESET}")
            sys.exit(1)

    def display_banner(self):
        print(f"{CYAN}┌──────────────────────────────────────────────────────────┐{RESET}")
        print(f"{CYAN}│       Advanced Recon Tool v2.5 - Bug Bounty Edition      │{RESET}")
        print(f"{CYAN}└──────────────────────────────────────────────────────────┘{RESET}")
        print(f"{BLUE}Date: {datetime.now()} | Mode: {self.mode} | Output: {self.output_dir}{RESET}")
        print()

    def update_checklist(self, step, status):
        for i, checklist_step in enumerate(self.checklist):
            if checklist_step == step:
                self.checklist_status[i] = status
        self.display_checklist()

    def display_checklist(self):
        print(f"{CYAN}=== Recon Checklist ==={RESET}")
        for step, status in zip(self.checklist, self.checklist_status):
            color = GREEN if status == "Completed" else YELLOW if status == "Running" else RED if status == "Error" else BLUE
            symbol = "✔" if status == "Completed" else "⏳" if status == "Running" else "✘" if status == "Error" else " "
            print(f"{color}[{symbol}] {step}: {status}{RESET}")
        print()

    def log_error(self, tool, error):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logging.error(f"{tool}: {error}")
        self.skipped_tools.append(tool)
        print(f"{RED}[!] {tool} failed. Check {self.error_log} for details.{RESET}")

    def monitor_resources(self, process, tool):
        start_time = time.time()
        percent = 0
        print(f"{YELLOW}[*] Starting {tool}...{RESET}")
        try:
            while process.poll() is None:
                percent = min(percent + 10, 100)
                cpu = process.cpu_percent(interval=1.0)
                mem = process.memory_percent()
                if cpu > self.cpu_limit:
                    process.cpu_percent(interval=0.1)  # Throttle
                print(f"{CYAN}[*] {tool} | Progress: {percent}% | CPU: {cpu:.1f}% | MEM: {mem:.1f}%{RESET}")
                time.sleep(2)
            elapsed = time.time() - start_time
            print(f"{GREEN}[✔] {tool} Completed in {elapsed:.1f} seconds{RESET}")
        except psutil.NoSuchProcess:
            print(f"{YELLOW}[!] {tool} process terminated unexpectedly{RESET}")

    def run_command(self, tool, command, step=None, retries=2):
        attempt = 0
        while attempt <= retries:
            try:
                cmd = command
                if hasattr(self, 'current_target'):
                    cmd = command.format(
                        target=self.current_target,
                        output_dir=self.current_target_dir,
                        extra_args=self.config["tools"][tool].get(self.mode, ""),
                        wordlist=self.config["tools"][tool].get(self.mode, ""),
                        templates=self.config["tools"][tool].get(self.mode, ""),
                        sources=self.config["tools"][tool].get(self.mode, ""),
                        input_file=self.config["tools"][tool].get(self.mode, ""),
                        subdomain="{subdomain}",
                        subdomain_dir="{subdomain_dir}",
                        host="{host}",
                        port="{port}"
                    )
                process = psutil.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
                monitor_thread = threading.Thread(target=self.monitor_resources, args=(process, tool))
                monitor_thread.start()
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    self.log_error(tool, f"Timeout after {self.timeout} seconds")
                    if step:
                        self.update_checklist(step, "Error")
                    return False
                monitor_thread.join()
                if process.returncode != 0:
                    error = stderr.decode().strip()
                    if "api key" in error.lower():
                        error = f"Missing or invalid API key for {tool}"
                    if attempt < retries:
                        print(f"{YELLOW}[!] {tool} failed, retrying ({attempt+1}/{retries})...{RESET}")
                        attempt += 1
                        time.sleep(1)
                        continue
                    self.log_error(tool, error)
                    if step:
                        self.update_checklist(step, "Error")
                    return False
                return True
            except Exception as e:
                if attempt < retries:
                    print(f"{YELLOW}[!] {tool} failed, retrying ({attempt+1}/{retries})...{RESET}")
                    attempt += 1
                    time.sleep(1)
                    continue
                self.log_error(tool, str(e))
                if step:
                    self.update_checklist(step, "Error")
                return False
            finally:
                try:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                except:
                    pass

    def setup_directories(self, target):
        self.current_target = target
        target_safe = re.sub(r"[*./]", "_", target)
        self.current_target_dir = self.output_dir / target_safe
        for subdir in ["subdomains", "ports", "services", "web_scans", "osint", "screenshots", "github"]:
            (self.current_target_dir / subdir).mkdir(parents=True, exist_ok=True)

    def install_dependencies(self):
        print(f"{YELLOW}[*] Checking and installing dependencies...{RESET}")
        dependencies = {
            "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            "amass": "go install -v github.com/OWASP/Amass/v3/...@master",
            "assetfinder": "go install github.com/tomnomnom/assetfinder@latest",
            "findomain": "wget -q https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux -O /usr/local/bin/findomain && chmod +x /usr/local/bin/findomain || wget -q https://github.com/Findomain/Findomain/releases/latest/download/findomain-aarch64 -O /usr/local/bin/findomain && chmod +x /usr/local/bin/findomain",
            "dnsx": "go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest",
            "httprobe": "go install github.com/tomnomnom/httprobe@latest",
            "naabu": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
            "nmap": "sudo apt-get install -y nmap",
            "ffuf": "go install github.com/ffuf/ffuf@latest",
            "paramspider": "pip3 install paramspider",
            "nuclei": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
            "theharvester": "sudo apt-get install -y theharvester",
            "metagoofil": "pip3 install metagoofil",
            "gowitness": "go install github.com/sensepost/gowitness@latest",
            "sublist3r": "pip3 install sublist3r",
            "waybackurls": "go install github.com/tomnomnom/waybackurls@latest"
        }
        for tool, install_cmd in dependencies.items():
            if not shutil.which(tool):
                print(f"{YELLOW}[*] Installing {tool}...{RESET}")
                if not self.run_command(f"Install {tool}", install_cmd, retries=1):
                    print(f"{RED}[!] Failed to install {tool}. Continuing...{RESET}")

    def run_github_recon(self):
        self.update_checklist("GitHub Recon", "Running")
        dorks = [
            f"from:{self.current_target} api_key",
            f"from:{self.current_target} password",
            f"from:{self.current_target} DB_PASSWORD",
            f"{self.current_target} access_key",
            f"{self.current_target} secret_key",
            f"{self.current_target} .env"
        ]
        github_output = self.current_target_dir / "github/results.txt"
        try:
            with open(github_output, "w") as f:
                for dork in dorks:
                    url = f"https://github.com/search?q={requests.utils.quote(dork)}&type=code"
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
                    response = requests.get(url, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.text, "html.parser")
                    results = soup.find_all("div", class_="code-list-item")
                    if results:
                        f.write(f"Dork: {dork}\n")
                        for result in results[:5]:  # Limit to 5 results per dork
                            snippet = result.find("div", class_="blob-wrapper")
                            if snippet:
                                f.write(f"Result: {snippet.text.strip()[:500]}...\n\n")
                    else:
                        f.write(f"Dork: {dork}\nNo results found.\n\n")
            print(f"{GREEN}[✔] GitHub recon completed: {github_output}{RESET}")
        except Exception as e:
            self.log_error("github-dork", str(e))
            self.update_checklist("GitHub Recon", "Error")
        self.update_checklist("GitHub Recon", "Completed")

    def run_dnsdumpster(self):
        cmd = self.config["tools"]["dnsdumpster"]["command"].format(
            target=self.current_target,
            output_dir=self.current_target_dir
        )
        self.run_command("dnsdumpster", cmd, "Subdomain Enumeration")

    def run_recursive_subdomain_enumeration(self, subdomain, level=1, max_level=3):
        if level > max_level:
            return
        print(f"{BLUE}[*] Running recursive enumeration for {subdomain} (Level {level})...{RESET}")
        recursive_dir = self.current_target_dir / f"subdomains/recursive_level_{level}"
        recursive_dir.mkdir(exist_ok=True)
        for tool in ["subfinder", "crtsh"]:
            cmd = self.config["tools"][tool]["command"].replace("{output_dir}/subdomains/", f"{recursive_dir}/").format(
                target=subdomain,
                output_dir=self.current_target_dir,
                extra_args=self.config["tools"][tool].get(self.mode, ""),
                wordlist=self.config["tools"][tool].get(self.mode, ""),
                templates=self.config["tools"][tool].get(self.mode, ""),
                sources=self.config["tools"][tool].get(self.mode, ""),
                input_file=self.config["tools"][tool].get(self.mode, ""),
                subdomain="{subdomain}",
                subdomain_dir="{subdomain_dir}",
                host="{host}",
                port="{port}"
            )
            self.run_command(f"{tool} Recursive {subdomain}", cmd, "Subdomain Enumeration")
        all_recursive = recursive_dir / "all_subdomains.txt"
        with open(all_recursive, "w") as f:
            for file in recursive_dir.glob("*.txt"):
                with open(file) as sub_file:
                    f.write(sub_file.read())
        subprocess.run(f"sort -u {all_recursive} > {all_recursive}.tmp && mv {all_recursive}.tmp {all_recursive}", shell=True, check=True)
        validated_recursive = recursive_dir / "validated_subdomains.txt"
        cmd = self.config["tools"]["dnsx"]["command"].replace("{output_dir}/subdomains/all_subdomains.txt", str(all_recursive)).replace("{output_dir}/subdomains/validated_subdomains.txt", str(validated_recursive))
        self.run_command("dnsx Recursive", cmd, "Subdomain Enumeration")
        if validated_recursive.exists() and validated_recursive.stat().st_size > 0:
            with open(validated_recursive) as f:
                for sub in f:
                    self.run_recursive_subdomain_enumeration(sub.strip(), level + 1, max_level)

    def run_parallel_subdomain_enumeration(self, tools):
        def run_tool(tool):
            if self.config["tools"][tool].get(self.mode, False):
                return self.run_command(tool, self.config["tools"][tool]["command"], "Subdomain Enumeration")
            return True
        self.update_checklist("Subdomain Enumeration", "Running")
        with Pool(processes=len(tools)) as pool:
            results = pool.map(run_tool, tools)
        all_subdomains = self.current_target_dir / "subdomains/all_subdomains.txt"
        with open(all_subdomains, "w") as f:
            for file in self.current_target_dir.glob("subdomains/*.txt"):
                with open(file) as sub_file:
                    f.write(sub_file.read())
        subprocess.run(f"sort -u {all_subdomains} > {all_subdomains}.tmp && mv {all_subdomains}.tmp {all_subdomains}", shell=True, check=True)
        if self.run_command("dnsx", self.config["tools"]["dnsx"]["command"], "Subdomain Enumeration"):
            validated = self.current_target_dir / "subdomains/validated_subdomains.txt"
            if validated.exists() and validated.stat().st_size == 0:
                print(f"{YELLOW}[!] No valid subdomains found for {self.current_target}{RESET}")
        self.update_checklist("Subdomain Enumeration", "Completed")

    def run_subdomain_enumeration(self):
        passive_tools = ["subfinder", "amass_passive", "assetfinder", "findomain", "crtsh", "sublist3r", "waybackurls"]
        self.run_parallel_subdomain_enumeration(passive_tools)
        self.run_dnsdumpster()
        if self.mode == "deep":
            for tool in ["amass_active", "ffuf_subdomains"]:
                self.run_command(tool, self.config["tools"][tool]["command"], "Subdomain Enumeration")
            validated = self.current_target_dir / "subdomains/validated_subdomains.txt"
            if validated.exists() and validated.stat().st_size > 0:
                with open(validated) as f:
                    for subdomain in f:
                        self.run_recursive_subdomain_enumeration(subdomain.strip(), level=1, max_level=3)

    def run_port_scanning(self):
        self.update_checklist("Port Scanning", "Running")
        if self.run_command("naabu", self.config["tools"]["naabu"]["command"], "Port Scanning"):
            ports_file = self.current_target_dir / "ports/ports.txt"
            if ports_file.exists() and ports_file.stat().st_size == 0:
                print(f"{YELLOW}[!] No open ports found for {self.current_target}{RESET}")
        self.update_checklist("Port Scanning", "Completed")

    def run_service_enumeration(self):
        self.update_checklist("Service Enumeration", "Running")
        ports_file = self.current_target_dir / "ports/ports.txt"
        if ports_file.exists() and ports_file.stat().st_size > 0:
            with open(ports_file) as f:
                for line in f:
                    try:
                        host, port = line.strip().split(":")
                        if self.mode == "default" and port not in ["80", "443"]:
                            continue
                        cmd = self.config["tools"]["nmap"]["command"].format(
                            port=port, host=host, output_dir=self.current_target_dir
                        )
                        self.run_command(f"Nmap {host}:{port}", cmd, "Service Enumeration")
                    except ValueError:
                        self.log_error("nmap", f"Invalid port format: {line.strip()}")
        else:
            print(f"{YELLOW}[!] No ports to enumerate for {self.current_target}{RESET}")
        self.update_checklist("Service Enumeration", "Completed")

    def run_web_scanning(self):
        self.update_checklist("Web Scanning", "Running")
        if self.run_command("httprobe", self.config["tools"]["httprobe"]["command"], "Web Scanning"):
            web_subdomains = self.current_target_dir / "subdomains/web_subdomains.txt"
            if web_subdomains.exists() and web_subdomains.stat().st_size > 0:
                def scan_subdomain(subdomain):
                    subdomain = subdomain.strip()
                    subdomain_dir = self.current_target_dir / f"web_scans/{subdomain.replace('/', '_')}"
                    subdomain_dir.mkdir(exist_ok=True)
                    for tool in ["ffuf_content", "nuclei"]:
                        if self.config["tools"][tool].get(self.mode, False):
                            cmd = self.config["tools"][tool]["command"].format(
                                subdomain=subdomain, subdomain_dir=subdomain_dir
                            )
                            self.run_command(f"{tool} {subdomain}", cmd, "Web Scanning")
                    if self.mode == "deep":
                        cmd = self.config["tools"]["paramspider"]["command"].format(
                            subdomain=subdomain, subdomain_dir=subdomain_dir
                        )
                        self.run_command(f"Paramspider {subdomain}", cmd, "Web Scanning")
                with open(web_subdomains) as f:
                    with Pool(processes=4) as pool:
                        pool.map(scan_subdomain, f)
            else:
                print(f"{YELLOW}[!] No web subdomains found for {self.current_target}{RESET}")
        self.update_checklist("Web Scanning", "Completed")

    def run_osint(self):
        self.update_checklist("OSINT", "Running")
        self.run_command("theharvester", self.config["tools"]["theharvester"]["command"], "OSINT")
        if self.mode == "deep":
            self.run_command("metagoofil", self.config["tools"]["metagoofil"]["command"], "OSINT")
        self.update_checklist("OSINT", "Completed")

    def run_visual_recon(self):
        self.update_checklist("Visual Reconnaissance", "Running")
        web_subdomains = self.current_target_dir / "subdomains/web_subdomains.txt"
        if web_subdomains.exists() and web_subdomains.stat().st_size > 0:
            if self.mode == "default":
                with open(web_subdomains) as f:
                    top_subdomains = self.current_target_dir / "subdomains/web_subdomains_top.txt"
                    with open(top_subdomains, "w") as out:
                        for i, line in enumerate(f):
                            if i >= 10:
                                break
                            out.write(line)
            cmd = self.config["tools"]["gowitness"]["command"].format(
                output_dir=self.current_target_dir,
                input_file=self.config["tools"]["gowitness"][self.mode]
            )
            self.run_command("gowitness", cmd, "Visual Reconnaissance")
        else:
            print(f"{YELLOW}[!] No web subdomains for visual recon on {self.current_target}{RESET}")
        self.update_checklist("Visual Reconnaissance", "Completed")

    def generate_html_report(self):
        report_file = self.output_dir / "report.html"
        with open(report_file, "w") as f:
            f.write("<html><head><title>Recon Report</title>")
            f.write("<style>body{font-family:Arial,sans-serif;background:#121212;color:#e0e0e0;}")
            f.write("h1,h2,h3{color:#00e676;}table{border-collapse:collapse;width:100%;}")
            f.write("th,td{border:1px solid #444;padding:8px;text-align:left;}")
            f.write("th{background:#1b5e20;}a{color:#00e676;}pre{background:#1e1e1e;padding:10px;}</style></head><body>")
            f.write(f"<h1>Recon Report - {self.timestamp}</h1>")
            for target in self.targets:
                target_dir = self.output_dir / re.sub(r"[*./]", "_", target)
                f.write(f"<h2>Target: {target}</h2>")
                subdomains_file = target_dir / "subdomains/validated_subdomains.txt"
                if subdomains_file.exists() and subdomains_file.stat().st_size > 0:
                    with open(subdomains_file) as sf:
                        subdomains = sf.readlines()
                    f.write(f"<h3>Subdomains ({len(subdomains)})</h3><table>")
                    for sub in subdomains:
                        f.write(f"<tr><td>{sub.strip()}</td></tr>")
                    f.write("</table>")
                for level in range(1, 4):
                    recursive_file = target_dir / f"subdomains/recursive_level_{level}/validated_subdomains.txt"
                    if recursive_file.exists() and recursive_file.stat().st_size > 0:
                        with open(recursive_file) as rf:
                            subdomains = rf.readlines()
                        f.write(f"<h3>Level {level} Subdomains ({len(subdomains)})</h3><table>")
                        for sub in subdomains:
                            f.write(f"<tr><td>{sub.strip()}</td></tr>")
                        f.write("</table>")
                github_file = target_dir / "github/results.txt"
                if github_file.exists() and github_file.stat().st_size > 0:
                    with open(github_file) as gf:
                        f.write("<h3>GitHub Recon</h3><pre>")
                        f.write(gf.read())
                        f.write("</pre>")
                vuln_files = glob.glob(str(target_dir / "web_scans/*/nuclei.txt"))
                if vuln_files:
                    f.write("<h3>Vulnerabilities</h3><table><tr><th>Subdomain</th><th>Details</th></tr>")
                    for vf in vuln_files:
                        subdomain = Path(vf).parent.name
                        with open(vf) as v:
                            f.write(f"<tr><td>{subdomain}</td><td><pre>{v.read()}</pre></td></tr>")
                    f.write("</table>")
                screenshots = glob.glob(str(target_dir / "screenshots/*.png"))
                if screenshots:
                    f.write("<h3>Screenshots</h3>")
                    for img in screenshots:
                        rel_path = Path(img).relative_to(self.output_dir)
                        f.write(f"<img src='{rel_path}' width='200' style='margin:5px'/>")
                if self.error_log.exists() and self.error_log.stat().st_size > 0:
                    with open(self.error_log) as ef:
                        f.write("<h3>Errors</h3><pre>")
                        f.write(ef.read())
                        f.write("</pre>")
            f.write("</body></html>")
        print(f"{BLUE}[*] HTML report generated: {report_file}{RESET}")

    def run(self):
        self.display_banner()
        self.install_dependencies()
        for target in self.targets:
            print(f"{CYAN}=== Processing Target: {target} ==={RESET}")
            self.setup_directories(target)
            self.run_subdomain_enumeration()
            self.run_github_recon()
            self.run_port_scanning()
            self.run_service_enumeration()
            self.run_web_scanning()
            self.run_osint()
            self.run_visual_recon()
        if self.skipped_tools:
            print(f"{RED}=== Skipped Tools (Errors Occurred) ==={RESET}")
            for tool in sorted(set(self.skipped_tools)):
                print(f"{RED}[!] Retry with: {tool}{RESET}")
        self.generate_html_report()
        print(f"{GREEN}=== Reconnaissance Completed ==={RESET}")
        print(f"{BLUE}Results saved in: {self.output_dir}{RESET}")
        self.display_checklist()

def main():
    parser = argparse.ArgumentParser(description="Advanced Recon Tool for Bug Bounty Hunting")
    parser.add_argument("--target", help="Single target domain (e.g., example.com)")
    parser.add_argument("--list", help="File with list of target domains")
    parser.add_argument("--wildcard", help="Wildcard domain (e.g., *.example.com)")
    parser.add_argument("--wildcard-list", help="File with list of wildcard domains")
    parser.add_argument("--output", help="Output directory", default=f"~/recon/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    parser.add_argument("--mode", choices=["default", "deep"], default="default", help="Scan mode: default or deep")
    parser.add_argument("--config", default="config.json", help="Configuration file")
    parser.add_argument("--cpu-limit", type=int, default=80, help="CPU usage limit per tool (percentage)")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per command (seconds)")
    args = parser.parse_args()

    if not any([args.target, args.list, args.wildcard, args.wildcard_list]):
        print(f"{RED}Error: Specify --target, --list, --wildcard, or --wildcard-list{RESET}")
        sys.exit(1)

    targets = []
    if args.target:
        targets.append(args.target)
    elif args.list:
        with open(args.list) as f:
            targets.extend(line.strip() for line in f if line.strip())
    elif args.wildcard:
        targets.append(args.wildcard.lstrip("*."))
    elif args.wildcard_list:
        with open(args.wildcard_list) as f:
            targets.extend(line.strip().lstrip("*.") for line in f if line.strip())

    recon = ReconTool(targets, args.output, args.mode, args.config, args.cpu_limit, args.timeout)
    recon.run()

if __name__ == "__main__":
    main()