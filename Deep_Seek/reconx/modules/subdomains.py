import os
import time
import concurrent.futures
from core.utils import *
from core.error_handler import ErrorHandler

class SubdomainEnumerator:
    def __init__(self, target, mode, output_dir, error_handler):
        self.target = target
        self.mode = mode
        self.output_dir = output_dir
        self.error_handler = error_handler
        self.subdomains = set()
        self.live_subdomains = set()
        self.takeover_candidates = []
        self.errors = []
        
        # Create subdomains directory
        self.subdomain_dir = os.path.join(output_dir, "subdomains")
        create_directory(self.subdomain_dir)

    def run(self):
        try:
            # Phase 1: Passive enumeration
            self._run_passive_enumeration()
            
            # Phase 2: Active enumeration
            if self.mode == "deep":
                self._run_active_enumeration()
                
            # Phase 3: Process results
            self._process_results()
            
            # Phase 4: Live verification
            self._verify_live_subdomains()
            
            # Phase 5: Takeover detection
            if self.mode == "deep":
                self._detect_subdomain_takeovers()
                
            # Phase 6: Deep analysis
            if self.mode == "deep":
                self._perform_deep_analysis()
                
            return {
                "all_subdomains": list(self.subdomains),
                "live_subdomains": list(self.live_subdomains),
                "takeover_candidates": self.takeover_candidates
            }
            
        except Exception as e:
            return self.error_handler.handle_exception(e, "subdomain_enum", self.target)

    # Implementation of all enumeration methods with try/except blocks
    def _run_passive_enumeration(self):
        tools = [
            self._query_crtsh,
            self._run_subfinder,
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
                    error = self.error_handler.log_error(e, "passive_enum", self.target)
                    self.errors.append(error)

    def _run_active_enumeration(self):
        try:
            permutations = self._generate_subdomain_permutations()
            self._resolve_dns_bruteforce(permutations)
        except Exception as e:
            error = self.error_handler.log_error(e, "active_enum", self.target)
            self.errors.append(error)

    # All other methods follow similar pattern with error handling
    # ...