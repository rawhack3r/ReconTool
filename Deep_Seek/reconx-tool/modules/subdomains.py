import os
import subprocess
import concurrent.futures
from core.utils import run_command, format_domain_list, log_error

class SubdomainEnumerator:
    def __init__(self, target, mode, output_dir, 
                 resource_monitor, progress_tracker):
        self.target = target
        self.mode = mode
        self.output_dir = output_dir
        self.resource_monitor = resource_monitor
        self.progress_tracker = progress_tracker
        self.subdomains = set()
        self.errors = []
        
    def run(self):
        self.progress_tracker.start_module("subdomain_enumeration")
        
        # Passive enumeration
        self._run_passive_enumeration()
        
        # Active enumeration in deep mode
        if self.mode == 'deep':
            self._run_active_enumeration()
        
        # Process results
        subdomains = sorted(self.subdomains)
        output_file = os.path.join(self.output_dir, "subdomains.txt")
        with open(output_file, 'w') as f:
            f.write("\n".join(subdomains))
        
        self.progress_tracker.complete_module("subdomain_enumeration", len(subdomains))
        return subdomains
    
    def _run_passive_enumeration(self):
        tools = [
            self._run_subfinder,
            self._run_assetfinder,
            self._run_crtsh,
            self._run_amass_passive
        ]
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(tool) for tool in tools]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results = future.result()
                    if results:
                        self.subdomains.update(results)
                except Exception as e:
                    self.errors.append(str(e))
                    log_error(f"Subdomain enumeration error: {str(e)}")
    
    def _run_active_enumeration(self):
        tools = [
            self._run_amass_active,
            self._run_ffuf_bruteforce
        ]
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(tool) for tool in tools]
            for future in concurrent.futures.as_completed(futures):
                try:
                    results = future.result()
                    if results:
                        self.subdomains.update(results)
                except Exception as e:
                    self.errors.append(str(e))
                    log_error(f"Active subdomain enum error: {str(e)}")
    
    # Tool-specific methods
    def _run_subfinder(self):
        self.resource_monitor.start_task("subfinder")
        cmd = ["subfinder", "-d", self.target, "-silent"]
        output = run_command(cmd, timeout=300)
        self.resource_monitor.end_task("subfinder")
        return format_domain_list(output)
    
    def _run_assetfinder(self):
        self.resource_monitor.start_task("assetfinder")
        cmd = ["assetfinder", "--subs-only", self.target]
        output = run_command(cmd, timeout=300)
        self.resource_monitor.end_task("assetfinder")
        return format_domain_list(output)
    
    # Other tool methods follow similar patterns...