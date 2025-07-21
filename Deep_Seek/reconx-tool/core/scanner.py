import os
import time
import json
import concurrent.futures
from datetime import datetime
from collections import defaultdict
from core.monitor import ResourceMonitor
from core.progress import ProgressTracker
from core.utils import format_output, create_directory
from modules.subdomains import SubdomainEnumerator
from modules.content import ContentDiscoverer
from modules.vulnerabilities import VulnerabilityScanner
from modules.reporting import ReportGenerator

class ReconScanner:
    def __init__(self, target, target_list, mode, output_dir, 
                 concurrency=10, max_resources=False):
        self.targets = self._load_targets(target, target_list)
        self.mode = mode
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.max_resources = max_resources
        self.resource_monitor = ResourceMonitor()
        self.progress_tracker = ProgressTracker()
        self.results = defaultdict(dict)
        self.errors = []
        self.start_time = time.time()
        
    def _load_targets(self, target, target_list):
        targets = []
        if target:
            targets.append(target)
        if target_list and os.path.exists(target_list):
            with open(target_list, 'r') as f:
                targets.extend(line.strip() for line in f if line.strip())
        return list(set(targets))
    
    def run(self):
        self.progress_tracker.start_scan(len(self.targets))
        
        # Process targets
        for i, target in enumerate(self.targets):
            self.progress_tracker.start_target(target, i+1)
            self._scan_target(target)
            self.progress_tracker.complete_target(target)
        
        self.progress_tracker.complete_scan()
    
    def _scan_target(self, target):
        # Create output directory
        target_dir = os.path.join(self.output_dir, target)
        create_directory(target_dir)
        
        # Initialize modules
        subdomain_enum = SubdomainEnumerator(
            target, self.mode, target_dir, 
            self.resource_monitor, self.progress_tracker
        )
        content_disc = ContentDiscoverer(
            target, self.mode, target_dir,
            self.resource_monitor, self.progress_tracker
        )
        vuln_scanner = VulnerabilityScanner(
            target, self.mode, target_dir,
            self.resource_monitor, self.progress_tracker
        )
        
        # Execute modules
        try:
            # Phase 1: Subdomain enumeration
            subdomains = subdomain_enum.run()
            self.results[target]['subdomains'] = subdomains
            self.results[target]['subdomain_count'] = len(subdomains)
            
            # Phase 2: Content discovery
            content_data = content_disc.run(subdomains)
            self.results[target].update(content_data)
            
            # Phase 3: Vulnerability scanning (deep mode only)
            if self.mode == 'deep':
                vulnerabilities = vuln_scanner.run(content_data['urls'])
                self.results[target]['vulnerabilities'] = vulnerabilities
                
        except Exception as e:
            self.errors.append(f"{target} scan failed: {str(e)}")
            self.progress_tracker.add_error(target, str(e))
    
    def generate_report(self):
        report_gen = ReportGenerator(
            self.results, 
            self.output_dir,
            self.mode,
            scan_duration=time.time() - self.start_time,
            errors=self.errors
        )
        report_path = report_gen.generate()
        self.progress_tracker.report_generated(report_path)