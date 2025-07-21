import os
import asyncio
import json
import shutil
import subprocess
import time
import redis
import pickle
import requests  # Add missing import
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from . import utils
from .state_manager import StateManager
from .error_handler import ErrorHandler
from .report_generator import generate_html_report, generate_pdf_report
from .ml_analyzer import MLVulnerabilityAnalyzer
from .distributed import DistributedScanner

class NightOwlOrchestrator:
    TOOL_BINARIES = {
        "amass": "amass",
        "assetfinder": "assetfinder",
        "sublist3r": "sublist3r",
        "subfinder": "subfinder",
        "findomain": "findomain",
        "crt_sh": "curl",
        "chaos": "chaos",
        "dnsrecon": "dnsrecon",
        "shuffledns": "shuffledns",
        "altdns": "altdns",
        "massdns": "massdns",
        "dirsearch": "dirsearch",
        "ffuf": "ffuf",
        "gospider": "gospider",
        "jsanalyzer": "katana",
        "wayback": "waybackurls",
        "gau": "gau",
        "hakrawler": "hakrawler",
        "nuclei": "nuclei",
        "zap": "zap-cli",
        "wpscan": "wpscan",
        "testssl": "testssl.sh",
        "takeover": "curl",
        "naabu": "naabu",
        "masscan": "masscan",
        "mobsf": "mobsfscan"
    }
    
    def __init__(self, target, mode, target_type, custom_tools, output_dir, dashboard, resume=False, verbose=False, distributed=False):
        self.target = target
        self.mode = mode
        self.target_type = target_type
        self.custom_tools = custom_tools
        self.output_dir = output_dir
        self.dashboard = dashboard
        self.resume = resume
        self.verbose = verbose
        self.distributed = distributed
        self.state = StateManager.load_state(target) if resume else {}
        self.error_handler = ErrorHandler()
        self.utils = utils.NightOwlUtils()
        self.ml_analyzer = MLVulnerabilityAnalyzer()
        self.distributed_scanner = DistributedScanner()
        
        self.tool_map = {
            "subdomain": {
                "amass": self.run_amass,
                "assetfinder": self.run_assetfinder,
                "sublist3r": self.run_sublist3r,
                "subfinder": self.run_subfinder,
                "findomain": self.run_findomain,
                "crt_sh": self.run_crt_sh,
                "chaos": self.run_chaos,
                "dnsrecon": self.run_dnsrecon,
                "recursive": self.run_recursive_enum
            },
            "content": {
                "dirsearch": self.run_dirsearch,
                "ffuf": self.run_ffuf,
                "gospider": self.run_gospider,
                "jsanalyzer": self.run_jsanalyzer
            },
            "info": {
                "wayback": self.run_wayback,
                "gau": self.run_gau,
                "hakrawler": self.run_hakrawler,
                "email": self.run_email_extractor,
                "secret": self.run_secret_finder,
                "pii": self.run_pii_extractor,
                "bucket": self.run_bucket_finder
            },
            "vuln": {
                "nuclei": self.run_nuclei,
                "zap": self.run_zap,
                "wpscan": self.run_wpscan,
                "testssl": self.run_testssl,
                "takeover": self.run_takeover
            },
            "network": {
                "naabu": self.run_naabu,
                "masscan": self.run_masscan
            },
            "mobile": {
                "mobsf": self.run_mobile_analysis
            }
        }
        
        self.verify_tools()
    
    def verify_tools(self):
        for category, tools in self.tool_map.items():
            for tool in tools:
                binary = self.TOOL_BINARIES.get(tool)
                if binary:
                    if shutil.which(binary) is None:
                        self.dashboard.skip_tool(tool, f"{binary} not installed")
                    else:
                        self.dashboard.show_info(f"{tool} verified: {binary} found")
    
    async def execute_workflow(self):
        phases = [
            {"name": "Initialization", "tools": [], "func": self.initialize},
            {"name": "Subdomain Enumeration", "tools": self.get_tools("subdomain"), "func": self.run_subdomain_tools},
            {"name": "Live Host Checking", "tools": [], "func": self.check_live_hosts},
            {"name": "Network Scanning", "tools": self.get_tools("network"), "func": self.run_network_tools},
            {"name": "Content Discovery", "tools": self.get_tools("content"), "func": self.run_content_tools},
            {"name": "Information Gathering", "tools": self.get_tools("info"), "func": self.run_info_tools},
            {"name": "Vulnerability Scanning", "tools": self.get_tools("vuln"), "func": self.run_vuln_tools},
            {"name": "Mobile Analysis", "tools": self.get_tools("mobile"), "func": self.run_mobile_tools},
            {"name": "Analysis & Reporting", "tools": [], "func": self.generate_reports}
        ]
        
        for idx, phase in enumerate(phases):
            self.dashboard.start_phase(idx)
            await phase["func"](phase["tools"])
            self.dashboard.complete_phase(idx)
            StateManager.save_state(self.target, self.state)
    
    def get_tools(self, category):
        if self.mode == "light":
            return ["assetfinder", "sublist3r", "crt_sh"]
        elif self.mode == "deep":
            return ["amass", "subfinder", "findomain", "dirsearch", "ffuf", "wayback", "email", "secret", "nuclei"]
        elif self.mode == "deeper":
            return list(self.tool_map[category].keys())
        else:  # custom
            return [tool for tool in self.custom_tools if tool in self.tool_map[category]]
    
    async def initialize(self, tools):
        self.dashboard.show_info("Creating output directories...")
        os.makedirs(f"{self.output_dir}/subdomains", exist_ok=True)
        os.makedirs(f"{self.output_dir}/live_hosts", exist_ok=True)
        os.makedirs(f"{self.output_dir}/content", exist_ok=True)
        os.makedirs(f"{self.output_dir}/info", exist_ok=True)
        os.makedirs(f"{self.output_dir}/vulns", exist_ok=True)
        os.makedirs(f"{self.output_dir}/reports", exist_ok=True)
        os.makedirs(f"{self.output_dir}/network", exist_ok=True)
        os.makedirs(f"{self.output_dir}/mobile", exist_ok=True)
        self.state = {
            "target": self.target,
            "mode": self.mode,
            "start_time": datetime.now().isoformat(),
            "phases": {}
        }
    
    async def run_subdomain_tools(self, tools):
        all_subdomains = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.tool_map["subdomain"][tool]): tool for tool in tools}
            for future in as_completed(futures):
                tool = futures[future]
                try:
                    result = future.result()
                    if result:
                        all_subdomains.extend(result)
                        self.dashboard.complete_tool(tool, f"Found {len(result)} subdomains")
                except Exception as e:
                    self.error_handler.log_error(tool, str(e), self.target)
                    self.dashboard.tool_error(tool, str(e))
        
        all_subdomains = list(set(all_subdomains))
        with open(f"{self.output_dir}/subdomains/all.txt", "w") as f:
            f.write("\n".join(all_subdomains))
        
        self.state["subdomains"] = all_subdomains
        return all_subdomains
    
    async def check_live_hosts(self, tools):
        if not self.state.get("subdomains"):
            self.dashboard.show_warning("No subdomains to check")
            return []
        
        self.dashboard.show_info("Checking live hosts...")
        live_urls = self.utils.check_alive(self.state["subdomains"], f"{self.output_dir}/live_hosts")
        
        important = self.utils.get_important_domains(live_urls, f"{self.output_dir}/live_hosts")
        self.state["live_urls"] = live_urls
        self.dashboard.show_info(f"Found {len(live_urls)} live hosts ({len(important)} important)")
        return live_urls
    
    async def run_network_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs for network scanning")
            return
        
        results = {}
        for tool in tools:
            try:
                self.dashboard.start_tool(tool, f"Running network scan")
                results[tool] = self.tool_map["network"][tool]()
                self.dashboard.complete_tool(tool, f"Completed network scan")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
                self.dashboard.tool_error(tool, str(e))
        
        self.state["network"] = results
    
    async def run_content_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        results = {}
        for tool in tools:
            try:
                self.dashboard.start_tool(tool, f"Running content discovery")
                results[tool] = self.tool_map["content"][tool]()
                self.dashboard.complete_tool(tool, f"Completed content discovery")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
                self.dashboard.tool_error(tool, str(e))
        
        self.state["content"] = results
    
    async def run_info_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        results = {}
        for tool in tools:
            try:
                self.dashboard.start_tool(tool, f"Extracting information")
                results[tool] = self.tool_map["info"][tool]()
                self.dashboard.complete_tool(tool, f"Extracted {len(results[tool])} items")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
                self.dashboard.tool_error(tool, str(e))
        
        if "email" in results:
            with open(f"{self.output_dir}/info/emails.txt", "w") as f:
                f.write("\n".join(results["email"]))
        if "pii" in results:
            with open(f"{self.output_dir}/info/pii.txt", "w") as f:
                f.write("\n".join(results["pii"]))
        if "secret" in results:
            with open(f"{self.output_dir}/info/secrets.txt", "w") as f:
                f.write("\n".join(results["secret"]))
        
        self.state["info"] = results
    
    async def run_vuln_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        vulns = {}
        for tool in tools:
            try:
                self.dashboard.start_tool(tool, f"Scanning for vulnerabilities")
                vulns[tool] = self.tool_map["vuln"][tool]()
                self.dashboard.complete_tool(tool, f"Found {len(vulns[tool])} vulnerabilities")
                
                if vulns[tool]:
                    with open(f"{self.output_dir}/vulns/{tool}.txt", "w") as f:
                        f.write("\n".join(vulns[tool]))
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
                self.dashboard.tool_error(tool, str(e))
        
        self.state["vulns"] = vulns
    
    async def run_mobile_tools(self, tools):
        if not (self.target.endswith(".apk") or self.target.endswith(".ipa")):
            self.dashboard.show_warning("Mobile analysis skipped - not a mobile target")
            return
        
        results = {}
        for tool in tools:
            try:
                self.dashboard.start_tool(tool, f"Analyzing mobile application")
                results[tool] = self.tool_map["mobile"][tool]()
                self.dashboard.complete_tool(tool, f"Completed mobile analysis")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
                self.dashboard.tool_error(tool, str(e))
        
        self.state["mobile"] = results
    
    async def generate_reports(self, tools):
        self.dashboard.show_info("Analyzing results and generating reports...")
        
        generate_html_report(self.target, self.output_dir, self.state)
        generate_pdf_report(self.target, self.output_dir)
        self.generate_manual_checklist()
        self.generate_executive_summary()
        self.prioritize_vulnerabilities()
    
    def generate_manual_checklist(self):
        checklist = f"NightOwl Manual Testing Checklist\n{'='*50}\n\n"
        checklist += "Critical Areas to Verify:\n"
        checklist += "1. Authentication Flows\n"
        checklist += "2. Sensitive Data Exposure\n"
        checklist += "3. Injection Vulnerabilities\n"
        checklist += "4. Business Logic Flaws\n"
        checklist += "5. Mobile-Specific Checks\n\n"
        checklist += "Domains Requiring Special Attention:\n"
        
        if "live_urls" in self.state:
            important = [url for url in self.state["live_urls"] if any(kw in url for kw in ["admin", "api", "internal"])]
            for url in important[:10]:
                checklist += f"    - {url}\n"
        
        with open(f"{self.output_dir}/reports/manual_checklist.txt", "w") as f:
            f.write(checklist)
    
    def generate_executive_summary(self):
        summary = f"NightOwl Recon Summary for {self.target}\n{'='*50}\n\n"
        
        if "subdomains" in self.state:
            summary += f"Subdomains Discovered: {len(self.state['subdomains'])}\n"
        if "live_urls" in self.state:
            summary += f"Live Hosts: {len(self.state['live_urls'])}\n"
        if "vulns" in self.state:
            critical_vulns = sum(1 for vulns in self.state['vulns'].values() for vuln in vulns if "[CRITICAL]" in vuln or "[HIGH]" in vuln)
            summary += f"Critical Vulnerabilities: {critical_vulns}\n"
        if "info" in self.state:
            if "email" in self.state["info"]:
                summary += f"Emails Found: {len(self.state['info']['email'])}\n"
            if "pii" in self.state["info"]:
                summary += f"PII Found: {len(self.state['info']['pii'])}\n"
        
        with open(f"{self.output_dir}/reports/summary.txt", "w") as f:
            f.write(summary)
    
    def prioritize_vulnerabilities(self):
        if "vulns" not in self.state:
            return
        
        vuln_data = []
        for tool, vulns in self.state["vulns"].items():
            for vuln in vulns:
                vuln_data.append({
                    "description": vuln,
                    "severity": "critical" if "[CRITICAL]" in vuln else "high" if "[HIGH]" in vuln else "medium"
                })
        
        self.ml_analyzer.train(vuln_data)
        
        prioritized_vulns = {"critical": [], "high": [], "medium": [], "low": []}
        for vuln in vuln_data:
            predicted_severity = self.ml_analyzer.predict_severity(vuln["description"])
            prioritized_vulns[predicted_severity].append(vuln["description"])
        
        for severity, vulns in prioritized_vulns.items():
            with open(f"{self.output_dir}/vulns/prioritized_{severity}.txt", "w") as f:
                f.write("\n".join(vulns))
    
    # Tool implementations
    def run_amass(self):
        output_file = f"{self.output_dir}/subdomains/amass.txt"
        cmd = f"amass enum -passive -d {self.target} -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_assetfinder(self):
        output_file = f"{self.output_dir}/subdomains/assetfinder.txt"
        cmd = f"assetfinder -subs-only {self.target} > {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_sublist3r(self):
        output_file = f"{self.output_dir}/subdomains/sublist3r.txt"
        cmd = f"sublist3r -d {self.target} -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_subfinder(self):
        output_file = f"{self.output_dir}/subdomains/subfinder.txt"
        cmd = f"subfinder -d {self.target} -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_findomain(self):
        output_file = f"{self.output_dir}/subdomains/findomain.txt"
        cmd = f"findomain -t {self.target} -o"
        result = self.utils.run_command(cmd, verbose=self.verbose)
        if result:
            with open(output_file, "w") as f:
                f.write(result)
            return result.splitlines()
        return []
    
    def run_crt_sh(self):
        try:
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            subdomains = set()
            for cert in data:
                name = cert.get("name_value", "")
                if name and self.target in name:
                    for sub in name.split("\n"):
                        if sub.strip() and self.target in sub:
                            subdomains.add(sub.strip())
            
            output_file = f"{self.output_dir}/subdomains/crt_sh.txt"
            with open(output_file, "w") as f:
                f.write("\n".join(subdomains))
            
            return list(subdomains)
        except:
            return []
    
    def run_chaos(self):
        try:
            url = f"https://dns.projectdiscovery.io/dns/{self.target}/subdomains"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            subdomains = [f"{sub}.{self.target}" for sub in data.get("subdomains", [])]
            
            output_file = f"{self.output_dir}/subdomains/chaos.txt"
            with open(output_file, "w") as f:
                f.write("\n".join(subdomains))
            
            return subdomains
        except:
            return []
    
    def run_dnsrecon(self):
        output_file = f"{self.output_dir}/subdomains/dnsrecon.txt"
        cmd = f"dnsrecon -d {self.target} -t std -j {output_file}"
        result = self.utils.run_command(cmd, verbose=self.verbose)
        
        # Parse JSON output
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            subdomains = [record['name'] for record in data if 'name' in record]
            with open(f"{self.output_dir}/subdomains/dnsrecon.txt", "w") as f:
                f.write("\n".join(subdomains))
            return subdomains
        except:
            return []
    
    def run_recursive_enum(self):
        if not self.state.get("subdomains"):
            return []
        
        candidate_domains = [d for d in self.state["subdomains"] if d.count('.') < 4]
        new_subdomains = []
        
        for domain in candidate_domains:
            if len(domain) > 30 or not any(kw in domain for kw in ["dev", "staging", "test"]):
                continue
                
            cmd = f"subfinder -d {domain} -silent"
            result = self.utils.run_command(cmd, verbose=self.verbose)
            if result:
                new_subdomains.extend(result.splitlines())
        
        return new_subdomains
    
    def run_dirsearch(self):
        input_file = f"{self.output_dir}/live_hosts/urls.txt"
        with open(input_file, "w") as f:
            f.write("\n".join(self.state["live_urls"]))
        
        output_file = f"{self.output_dir}/content/dirsearch.txt"
        cmd = f"dirsearch -l {input_file} --format=plain -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_ffuf(self):
        wordlist = "config/wordlists/directories.txt"
        output_file = f"{self.output_dir}/content/ffuf.txt"
        results = []
        
        for url in self.state["live_urls"]:
            cmd = f"ffuf -w {wordlist} -u {url}/FUZZ -o {output_file} -of json"
            result = self.utils.run_command(cmd, verbose=self.verbose)
            if result:
                try:
                    data = json.loads(result)
                    for item in data.get("results", []):
                        results.append(f"{url}{item['url']}")
                except:
                    continue
        
        return results
    
    def run_gospider(self):
        input_file = f"{self.output_dir}/live_hosts/urls.txt"
        with open(input_file, "w") as f:
            f.write("\n".join(self.state["live_urls"]))
        
        output_file = f"{self.output_dir}/content/gospider.txt"
        cmd = f"gospider -S {input_file} -o {output_file} -t 50"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_jsanalyzer(self):
        js_files = []
        for url in self.state["live_urls"]:
            cmd = f"katana -u {url} -js-crawl -jc -kf js"
            result = self.utils.run_command(cmd, verbose=self.verbose)
            if result:
                js_files.extend(result.splitlines())
        
        secrets = []
        for js_file in js_files:
            try:
                response = requests.get(js_file, timeout=5)
                content = response.text
                if "api" in content and "key" in content:
                    secrets.append(js_file)
            except:
                continue
        
        with open(f"{self.output_dir}/content/js_analysis.txt", "w") as f:
            f.write("\n".join(secrets))
        
        return secrets
    
    def run_wayback(self):
        output_file = f"{self.output_dir}/info/wayback.txt"
        cmd = f"waybackurls {self.target} > {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_gau(self):
        output_file = f"{self.output_dir}/info/gau.txt"
        cmd = f"gau {self.target} > {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_hakrawler(self):
        output_file = f"{self.output_dir}/info/hakrawler.txt"
        cmd = f"hakrawler -url {self.target} -depth 2 -plain > {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_email_extractor(self):
        content = "\n".join(self.state["live_urls"])
        return self.utils.extract_emails(content)
    
    def run_secret_finder(self):
        content = "\n".join(self.state["live_urls"])
        return self.utils.extract_secrets(content)
    
    def run_pii_extractor(self):
        content = "\n".join(self.state["live_urls"])
        emails = self.utils.extract_emails(content)
        phones = self.utils.extract_phones(content)
        names = self.utils.extract_names(content)
        return emails + phones + names
    
    def run_bucket_finder(self):
        return self.utils.find_buckets(self.state["subdomains"])
    
    def run_nuclei(self):
        input_file = f"{self.output_dir}/live_hosts/urls.txt"
        with open(input_file, "w") as f:
            f.write("\n".join(self.state["live_urls"]))
        
        output_file = f"{self.output_dir}/vulns/nuclei.txt"
        cmd = f"nuclei -l {input_file} -severity medium,high,critical -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_zap(self):
        if not self.state.get("live_urls"):
            return []
        
        output_file = f"{self.output_dir}/vulns/zap.json"
        cmd = f"zap-cli --zap-path /usr/share/zap -p 8090 quick-scan -o json -O {output_file} "
        cmd += " ".join(self.state["live_urls"])
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_wpscan(self):
        wp_sites = [url for url in self.state["live_urls"] if "wp-content" in url]
        if not wp_sites:
            return []
        
        results = []
        for site in wp_sites:
            output_file = f"{self.output_dir}/vulns/wpscan_{site.replace('://', '_')}.txt"
            cmd = f"wpscan --url {site} --output {output_file}"
            results.extend(self.utils.run_command(cmd, verbose=self.verbose))
        
        return results
    
    def run_testssl(self):
        if not self.state.get("live_urls"):
            return []
        
        results = []
        for url in self.state["live_urls"]:
            if not url.startswith("https://"):
                continue
            domain = url.replace("https://", "")
            output_file = f"{self.output_dir}/vulns/testssl_{domain}.txt"
            cmd = f"testssl.sh --quiet --color 0 {domain} > {output_file}"
            results.extend(self.utils.run_command(cmd, verbose=self.verbose))
        
        return results
    
    def run_takeover(self):
        if not self.state.get("subdomains"):
            return []
        
        vulnerable = []
        for subdomain in self.state["subdomains"]:
            try:
                response = requests.get(f"http://{subdomain}", timeout=5)
                if response.status_code == 404 and "404 Not Found" in response.text:
                    vulnerable.append(subdomain)
            except:
                continue
        
        with open(f"{self.output_dir}/vulns/takeover.txt", "w") as f:
            f.write("\n".join(vulnerable))
        
        return vulnerable
    
    def run_naabu(self):
        if not self.state.get("live_urls"):
            return []
        
        output_file = f"{self.output_dir}/network/naabu.txt"
        cmd = f"naabu -list {self.output_dir}/live_hosts/urls.txt -o {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_masscan(self):
        if not self.state.get("live_urls"):
            return []
        
        output_file = f"{self.output_dir}/network/masscan.txt"
        cmd = f"masscan -p1-65535 -iL {self.output_dir}/live_hosts/urls.txt -oG {output_file}"
        return self.utils.run_command(cmd, verbose=self.verbose, output_file=output_file)
    
    def run_mobile_analysis(self):
        if not (self.target.endswith(".apk") or self.target.endswith(".ipa")):
            return {}
        
        output_file = f"{self.output_dir}/mobile/mobsf.json"
        cmd = f"mobsfscan {self.target} --json -o {output_file}"
        result = self.utils.run_command(cmd, verbose=self.verbose)
        if result and os.path.exists(output_file):
            with open(output_file, "r") as f:
                return json.load(f)
        return {}
