class NightOwlChecklist:
    def __init__(self, scan_results):
        self.results = scan_results
    
    def generate(self):
        return {
            "critical_vulnerabilities": self._get_critical_vulns(),
            "exposed_credentials": self._get_exposed_credentials(),
            "cloud_misconfigs": self._get_cloud_misconfigs(),
            "attack_surface": self._get_attack_surface_items(),
            "blockchain_risks": self._get_blockchain_risks(),
            "next_steps": self._get_next_steps()
        }
    
    def _get_critical_vulns(self):
        return [
            vuln for vuln in self.results.get('vulnerabilities', [])
            if vuln['severity'] in ['critical', 'high']
        ]
    
    def _get_exposed_credentials(self):
        return self.results.get('information', {}).get('secrets', [])
    
    def _get_cloud_misconfigs(self):
        misconfigs = []
        for provider in ['AWS', 'Azure', 'GCP']:
            misconfigs.extend(
                self.results.get('cloud', {}).get(provider, {}).get('misconfigurations', [])
            )
        return misconfigs
    
    def _get_attack_surface_items(self):
        return self.results.get('attack_surface', {}).get('critical_paths', [])
    
    def _get_blockchain_risks(self):
        return [
            addr for addr, data in self.results.get('blockchain', {}).items()
            if data['risk_score'] > 70
        ]
    
    def _get_next_steps(self):
        steps = ["Review critical vulnerabilities"]
        
        if self._get_exposed_credentials():
            steps.append("Rotate exposed credentials immediately")
        
        if self._get_cloud_misconfigs():
            steps.append("Remediate cloud misconfigurations")
        
        if self._get_attack_surface_items():
            steps.append("Analyze critical attack paths")
        
        if self._get_blockchain_risks():
            steps.append("Investigate high-risk blockchain addresses")
        
        steps.extend([
            "Perform manual penetration testing on critical systems",
            "Implement WAF rules for identified attack patterns",
            "Schedule rescan after remediation"
        ])
        
        return steps