import asyncio
import os
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from core import utils
from core.state_manager import StateManager
from core.error_handler import ErrorHandler
from core.report_generator import generate_html_report
from core.checklist import generate_manual_checklist
from core.analyzer import analyze_results

class NightOwlOrchestrator:
    def __init__(self, target, mode, target_type, custom_tools, output_dir, dashboard, resume=False, verbose=False):
        self.target = target
        self.mode = mode
        self.target_type = target_type
        self.custom_tools = custom_tools
        self.output_dir = output_dir
        self.dashboard = dashboard
        self.resume = resume
        self.verbose = verbose
        self.state = StateManager.load_state(target) if resume else {}
        self.error_handler = ErrorHandler()
        self.utils = utils.Utils()
        
        # Tool mappings
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
                "shuffledns": self.run_shuffledns,
                "altdns": self.run_altdns,
                "massdns": self.run_massdns
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
            }
        }
    
    async def execute_workflow(self):
        phases = [
            {"name": "Initialization", "tools": [], "func": self.initialize},
            {"name": "Subdomain Enumeration", "tools": self.get_tools("subdomain"), "func": self.run_subdomain_tools},
            {"name": "Live Host Checking", "tools": [], "func": self.check_live_hosts},
            {"name": "Network Scanning", "tools": self.get_tools("network"), "func": self.run_network_tools},
            {"name": "Content Discovery", "tools": self.get_tools("content"), "func": self.run_content_tools},
            {"name": "Information Gathering", "tools": self.get_tools("info"), "func": self.run_info_tools},
            {"name": "Vulnerability Scanning", "tools": self.get_tools("vuln"), "func": self.run_vuln_tools},
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
                        self.dashboard.show_info(f"{tool}: Found {len(result)} subdomains")
                except Exception as e:
                    self.error_handler.log_error(tool, str(e), self.target)
        
        # Save and deduplicate results
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
        
        # Categorize results
        important = self.utils.get_important_domains(live_urls, f"{self.output_dir}/live_hosts")
        self.state["live_urls"] = live_urls
        self.dashboard.show_info(f"Found {len(live_urls)} live hosts ({len(important)} important)")
        return live_urls
    
    async def run_network_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs for network scanning")
            return
        
        # Run network scanning tools
        results = {}
        for tool in tools:
            try:
                results[tool] = self.tool_map["network"][tool]()
                self.dashboard.show_info(f"{tool}: Completed network scan")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
        
        self.state["network"] = results
    
    async def run_content_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        # Run content discovery tools
        results = {}
        for tool in tools:
            try:
                results[tool] = self.tool_map["content"][tool]()
                self.dashboard.show_info(f"{tool}: Completed content discovery")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
        
        self.state["content"] = results
    
    async def run_info_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        # Run information extraction tools
        results = {}
        for tool in tools:
            try:
                results[tool] = self.tool_map["info"][tool]()
                self.dashboard.show_info(f"{tool}: Extracted {len(results[tool])} items")
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
        
        # Save PII separately
        if "email" in results:
            with open(f"{self.output_dir}/info/emails.txt", "w") as f:
                f.write("\n".join(results["email"]))
        if "pii" in results:
            with open(f"{self.output_dir}/info/pii.txt", "w") as f:
                f.write("\n".join(results["pii"]))
        
        self.state["info"] = results
    
    async def run_vuln_tools(self, tools):
        if not self.state.get("live_urls"):
            self.dashboard.show_warning("No live URLs to scan")
            return
        
        # Run vulnerability scanners
        vulns = {}
        for tool in tools:
            try:
                vulns[tool] = self.tool_map["vuln"][tool]()
                self.dashboard.show_info(f"{tool}: Found {len(vulns[tool])} vulnerabilities")
                
                # Save critical vulnerabilities
                if vulns[tool]:
                    with open(f"{self.output_dir}/vulns/{tool}.txt", "w") as f:
                        f.write("\n".join(vulns[tool]))
            except Exception as e:
                self.error_handler.log_error(tool, str(e), self.target)
        
        self.state["vulns"] = vulns
    
    async def generate_reports(self, tools):
        self.dashboard.show_info("Analyzing results and generating reports...")
        
        # Generate HTML report
        generate_html_report(
            self.target,
            self.output_dir,
            f"{self.output_dir}/reports/report.html"
        )
        
        # Generate manual checklist
        checklist = generate_manual_checklist(self.state)
        with open(f"{self.output_dir}/reports/manual_checklist.txt", "w") as f:
            f.write(checklist)
        
        # Generate executive summary
        analyze_results(self.state, f"{self.output_dir}/reports/summary.txt")
    
    # Tool execution methods
    def run_amass(self):
        from tools.subdomain.amass import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_assetfinder(self):
        from tools.subdomain.assetfinder import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_subfinder(self):
        from tools.subdomain.subfinder import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_findomain(self):
        from tools.subdomain.findomain import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_crt_sh(self):
        from tools.subdomain.crt_sh import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_chaos(self):
        from tools.subdomain.chaos import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_dnsrecon(self):
        from tools.subdomain.dnsrecon import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_shuffledns(self):
        from tools.subdomain.shuffledns import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_altdns(self):
        from tools.subdomain.altdns import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_massdns(self):
        from tools.subdomain.massdns import run
        return run(self.target, f"{self.output_dir}/subdomains")
    
    def run_dirsearch(self):
        from tools.content.dirsearch import run
        return run(self.state["live_urls"], f"{self.output_dir}/content")
    
    def run_ffuf(self):
        from tools.content.ffuf import run
        return run(self.state["live_urls"], f"{self.output_dir}/content")
    
    def run_gospider(self):
        from tools.content.gospider import run
        return run(self.state["live_urls"], f"{self.output_dir}/content")
    
    def run_jsanalyzer(self):
        from tools.content.jsanalyzer import run
        return run(self.state["live_urls"], f"{self.output_dir}/content")
    
    def run_wayback(self):
        from tools.information.wayback import run
        return run(self.target, f"{self.output_dir}/info")
    
    def run_gau(self):
        from tools.information.gau import run
        return run(self.target, f"{self.output_dir}/info")
    
    def run_hakrawler(self):
        from tools.information.hakrawler import run
        return run(self.target, f"{self.output_dir}/info")
    
    def run_email_extractor(self):
        from tools.information.email_extractor import run
        return run("\n".join(self.state["live_urls"]))
    
    def run_secret_finder(self):
        from tools.information.secret_finder import run
        return run("\n".join(self.state["live_urls"]))
    
    def run_pii_extractor(self):
        from tools.information.pii_extractor import run
        return run("\n".join(self.state["live_urls"]))
    
    def run_bucket_finder(self):
        from tools.information.bucket_finder import run
        return run(self.state["subdomains"])
    
    def run_nuclei(self):
        from tools.vulnerability.nuclei import run
        return run(self.state["live_urls"], f"{self.output_dir}/vulns")
    
    def run_zap(self):
        from tools.vulnerability.zap import run
        return run(self.state["live_urls"], f"{self.output_dir}/vulns")
    
    def run_wpscan(self):
        from tools.vulnerability.wpscan import run
        return run(self.state["live_urls"], f"{self.output_dir}/vulns")
    
    def run_testssl(self):
        from tools.vulnerability.testssl import run
        return run(self.state["live_urls"], f"{self.output_dir}/vulns")
    
    def run_takeover(self):
        from tools.vulnerability.takeover import run
        return run(self.state["subdomains"], f"{self.output_dir}/vulns")
    
    def run_naabu(self):
        from tools.network.naabu import run
        return run(self.state["live_urls"], f"{self.output_dir}/network")
    
    def run_masscan(self):
        from tools.network.masscan import run
        return run(self.state["live_urls"], f"{self.output_dir}/network")