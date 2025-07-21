import networkx as nx
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

class ThreatCorrelationEngine:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.entity_map = defaultdict(list)
        self.temporal_window = timedelta(days=7)
    
    def ingest_scan_results(self, scan_data):
        # Process subdomains
        for domain_data in scan_data.get('subdomains', {}).values():
            for domain in domain_data.get('result', {}).get('subdomains', []):
                domain_name = self.normalize_domain(domain['domain'])
                self.graph.add_node(domain_name, type='domain', criticality=3)
                
                if 'resolved_ips' in domain:
                    for ip in domain['resolved_ips']:
                        self.graph.add_node(ip, type='ip', criticality=5)
                        self.graph.add_edge(domain_name, ip, relationship='resolves_to')
        
        # Process vulnerabilities
        for vuln_data in scan_data.get('vulnerabilities', {}).values():
            for vuln in vuln_data.get('result', {}).get('vulnerabilities', []):
                criticality = self.vuln_criticality(vuln.get('severity', 'medium'))
                self.graph.add_node(vuln['url'], type='vulnerability', criticality=criticality, **vuln)
                self.graph.add_edge(vuln['url'], vuln['host'], relationship='affects')
        
        # Process cloud assets
        for asset in scan_data.get('cloud_assets', []):
            self.graph.add_node(asset['id'], type='cloud_asset', criticality=8, **asset)
    
    def vuln_criticality(self, severity):
        return {
            'critical': 10,
            'high': 8,
            'medium': 6,
            'low': 4,
            'info': 2
        }.get(severity.lower(), 5)
    
    def normalize_domain(self, domain):
        return domain.lower().strip().replace('*.', '')
    
    def temporal_correlation(self, new_scan, historical_scans):
        anomalies = []
        
        # Subdomain growth anomaly
        current_count = len(new_scan.get('subdomains', []))
        historical_counts = [len(scan.get('subdomains', [])) for scan in historical_scans]
        
        if historical_counts:
            mean_count = np.mean(historical_counts)
            std_dev = np.std(historical_counts)
            if current_count > mean_count + (3 * std_dev):
                anomalies.append({
                    "type": "subdomain_growth",
                    "current": current_count,
                    "historical_avg": mean_count,
                    "std_dev": std_dev,
                    "severity": 8
                })
        
        # Vulnerability spike detection
        current_critical = sum(1 for v in new_scan.get('vulnerabilities', []) 
                              if self.vuln_criticality(v.get('severity')) >= 8)
        historical_critical = [sum(1 for v in scan.get('vulnerabilities', []) 
                              if self.vuln_criticality(v.get('severity')) >= 8) 
                              for scan in historical_scans]
        
        if historical_critical:
            mean_critical = np.mean(historical_critical)
            if current_critical > mean_critical * 2:
                anomalies.append({
                    "type": "critical_vuln_spike",
                    "current": current_critical,
                    "historical_avg": mean_critical,
                    "severity": 9
                })
                
        return anomalies
    
    def identify_attack_paths(self, target):
        target_node = self.normalize_domain(target)
        if target_node not in self.graph:
            return []
            
        critical_assets = [n for n, data in self.graph.nodes(data=True) 
                          if data.get('criticality', 0) >= 8]
        
        attack_paths = []
        for asset in critical_assets:
            try:
                path = nx.shortest_path(self.graph, source=target_node, target=asset)
                attack_paths.append({
                    "source": target_node,
                    "target": asset,
                    "path": path,
                    "length": len(path),
                    "criticality": self.calculate_path_risk(path)
                })
            except nx.NetworkXNoPath:
                continue
        
        return sorted(attack_paths, key=lambda x: x['criticality'], reverse=True)[:5]
    
    def calculate_path_risk(self, path):
        risk = 0
        for node in path:
            node_data = self.graph.nodes[node]
            risk += node_data.get('criticality', 0)
            
            # Add bonus for cloud assets
            if node_data.get('type') == 'cloud_asset':
                risk += 3
        return risk