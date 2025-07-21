import os
import time
import random
from core.utils import create_directory, http_request
from core.error_handler import ErrorHandler

class VulnerabilityScanner:
    def __init__(self, target, output_dir, error_handler):
        self.target = target
        self.output_dir = output_dir
        self.error_handler = error_handler
        self.vuln_dir = os.path.join(output_dir, "vulnerabilities")
        create_directory(self.vuln_dir)
    
    def run(self, urls):
        try:
            vulnerabilities = []
            
            # 1. Run Nuclei scans
            vulnerabilities.extend(self._run_nuclei_scans(urls))
            
            # 2. Check common vulnerabilities
            vulnerabilities.extend(self._check_common_vulns(urls))
            
            # 3. Specialized checks
            vulnerabilities.extend(self._check_special_vulns(urls))
            
            # Save results
            self._save_vulnerabilities(vulnerabilities)
            return vulnerabilities
            
        except Exception as e:
            return self.error_handler.handle_exception(e, "vulnerability_scan", self.target)
    
    def _run_nuclei_scans(self, urls):
        vulns = []
        try:
            # Simulate Nuclei scan
            templates = [
                "cves", "misconfigurations", "exposed-panels",
                "takeovers", "default-logins", "dns"
            ]
            for i in range(3):  # Simulate findings
                url = random.choice(urls)
                template = random.choice(templates)
                vulns.append({
                    'url': url,
                    'type': template.upper(),
                    'severity': random.choice(['Medium', 'High']),
                    'description': f"Nuclei detected {template} vulnerability",
                    'tool': 'Nuclei'
                })
                time.sleep(0.1)
            return vulns
        except Exception as e:
            self.error_handler.log_error(e, "nuclei_scan", self.target)
            return []
    
    def _check_common_vulns(self, urls):
        vulns = []
        try:
            # Simulate common vulnerability checks
            common_vulns = [
                "XSS", "SQL Injection", "SSRF", "IDOR", 
                "LFI", "RCE", "XXE", "Open Redirect"
            ]
            for url in urls[:5]:  # Limit for simulation
                if random.random() > 0.7:  # 30% chance of vulnerability
                    vuln_type = random.choice(common_vulns)
                    vulns.append({
                        'url': url,
                        'type': vuln_type,
                        'severity': random.choice(['Low', 'Medium', 'High']),
                        'description': f"Potential {vuln_type} vulnerability detected",
                        'tool': 'Custom Check'
                    })
                time.sleep(0.08)
            return vulns
        except Exception as e:
            self.error_handler.log_error(e, "common_vulns", self.target)
            return []
    
    def _check_special_vulns(self, urls):
        vulns = []
        try:
            # Simulate special vulnerability checks
            special_vulns = {
                "JWT": "Invalid signature validation",
                "CORS": "Misconfigured CORS policy",
                "CSP": "Missing Content Security Policy",
                "Clickjacking": "Missing X-Frame-Options header"
            }
            for url in urls[:3]:  # Limit for simulation
                if random.random() > 0.8:  # 20% chance of vulnerability
                    vuln_type = random.choice(list(special_vulns.keys()))
                    vulns.append({
                        'url': url,
                        'type': vuln_type,
                        'severity': random.choice(['Medium', 'High']),
                        'description': special_vulns[vuln_type],
                        'tool': 'Advanced Check'
                    })
                time.sleep(0.1)
            return vulns
        except Exception as e:
            self.error_handler.log_error(e, "special_vulns", self.target)
            return []
    
    def _save_vulnerabilities(self, vulnerabilities):
        try:
            # Save as JSON
            with open(os.path.join(self.vuln_dir, "vulnerabilities.json"), "w") as f:
                json.dump(vulnerabilities, f, indent=2)
            
            # Save as CSV
            with open(os.path.join(self.vuln_dir, "vulnerabilities.csv"), "w") as f:
                writer = csv.DictWriter(f, fieldnames=vulnerabilities[0].keys())
                writer.writeheader()
                writer.writerows(vulnerabilities)
        except Exception as e:
            self.error_handler.log_error(e, "vuln_saving", self.target)