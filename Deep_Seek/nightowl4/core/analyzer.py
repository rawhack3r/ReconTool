import re
import json
from .utils import NightOwlUtils

utils = NightOwlUtils()

class VulnerabilityAnalyzer:
    def __init__(self):
        self.patterns = utils.load_patterns()
    
    def analyze_vulnerabilities(self, vulns):
        critical = []
        high = []
        medium = []
        low = []
        
        for tool, findings in vulns.items():
            for finding in findings:
                if "[CRITICAL]" in finding or "Critical" in finding:
                    critical.append(f"{tool}: {finding}")
                elif "[HIGH]" in finding or "High" in finding:
                    high.append(f"{tool}: {finding}")
                elif "[MEDIUM]" in finding or "Medium" in finding:
                    medium.append(f"{tool}: {finding}")
                else:
                    low.append(f"{tool}: {finding}")
        
        return {
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low
        }
    
    def analyze_information(self, info):
        analysis = {}
        if "email" in info:
            analysis["email_domains"] = self.extract_email_domains(info["email"])
        if "pii" in info:
            analysis["pii_types"] = self.categorize_pii(info["pii"])
        return analysis
    
    def extract_email_domains(self, emails):
        domains = {}
        for email in emails:
            domain = email.split('@')[-1]
            domains[domain] = domains.get(domain, 0) + 1
        return domains
    
    def categorize_pii(self, pii_items):
        pii_types = {}
        patterns = self.patterns
        
        for item in pii_items:
            if re.match(patterns["emails"], item):
                pii_types["emails"] = pii_types.get("emails", 0) + 1
            elif re.match(patterns["phones"], item):
                pii_types["phones"] = pii_types.get("phones", 0) + 1
            elif re.match(patterns["names"], item):
                pii_types["names"] = pii_types.get("names", 0) + 1
            elif any(pattern in item for pattern in ["ssn", "social", "security"]):
                pii_types["ssn"] = pii_types.get("ssn", 0) + 1
            else:
                pii_types["other"] = pii_types.get("other", 0) + 1
        
        return pii_types