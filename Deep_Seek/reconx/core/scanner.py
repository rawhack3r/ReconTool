import os
import time
from collections import defaultdict
from modules.subdomains import SubdomainEnumerator
from modules.content import ContentDiscoverer
from modules.vulnerabilities import VulnerabilityScanner
from modules.reporting import ReportGenerator
from core.error_handler import ErrorHandler
from core.progress import ProgressTracker

class ReconScanner:
    def __init__(self, target, target_list, mode, output_dir, 
                 concurrency=10, max_resources=False):
        self.targets = self._load_targets(target, target_list)
        self.mode = mode
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.max_resources = max_resources
        self.error_handler = ErrorHandler(output_dir)
        self.progress_tracker = ProgressTracker()
        self.results = defaultdict(dict)
        self.errors = []
        self.start_time = time.time()
        
    def _load_targets(self, target, target_list):
        targets = []
        if target:
            targets.append(target)
        if target_list and os.path.exists(target_list):
            try:
                with open(target_list, 'r') as f:
                    targets.extend(line.strip() for line in f if line.strip())
            except Exception as e:
                self.error_handler.log_error(e, "scanner", "target_loading")
        return list(set(targets))
    
    def run(self):
        try:
            self.progress_tracker.start_scan(len(self.targets))
            
            for target in self.targets:
                self.progress_tracker.start_target(target)
                self._scan_target(target)
                self.progress_tracker.complete_target(target)
            
            self.progress_tracker.complete_scan()
            return True
        except Exception as e:
            self.error_handler.handle_exception(e, "scanner")
            return False
    
    def _scan_target(self, target):
        try:
            # Create target directory
            target_dir = os.path.join(self.output_dir, target)
            create_directory(target_dir)
            
            # Subdomain enumeration
            subdomain_enumerator = SubdomainEnumerator(
                target=target,
                mode=self.mode,
                output_dir=target_dir,
                error_handler=self.error_handler
            )
            subdomain_results = subdomain_enumerator.run()
            self.results[target].update(subdomain_results)
            
            # Content discovery
            content_discoverer = ContentDiscoverer(
                target=target,
                mode=self.mode,
                output_dir=target_dir,
                error_handler=self.error_handler
            )
            content_data = content_discoverer.run(subdomain_results["live_subdomains"])
            self.results[target].update(content_data)
            
            # Vulnerability scanning
            if self.mode == 'deep':
                vuln_scanner = VulnerabilityScanner(
                    target=target,
                    output_dir=target_dir,
                    error_handler=self.error_handler
                )
                vulnerabilities = vuln_scanner.run(content_data['urls'])
                self.results[target]['vulnerabilities'] = vulnerabilities
                
        except Exception as e:
            error = self.error_handler.handle_exception(e, "scan_target", target)
            self.errors.append(error)
            self.results[target]['scan_status'] = 'failed'
            self.results[target]['error'] = error
    
    def generate_report(self):
        try:
            report_gen = ReportGenerator(
                self.results, 
                self.output_dir,
                self.mode,
                scan_duration=time.time() - self.start_time,
                errors=self.errors
            )
            report_path = report_gen.generate()
            return report_path
        except Exception as e:
            self.error_handler.handle_exception(e, "report_generation")
            return None