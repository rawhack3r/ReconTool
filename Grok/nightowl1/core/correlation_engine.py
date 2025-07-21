import networkx as nx
from core.error_handler import ErrorHandler

class ThreatCorrelationEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, findings):
        for finding in findings:
            criticality = self.calculate_criticality(finding)
            self.graph.add_node(finding['id'], type=finding['type'], criticality=criticality)
            if 'related' in finding:
                for related in finding['related']:
                    self.graph.add_edge(finding['id'], related['id'])

    def calculate_criticality(self, finding):
        keywords = ["admin", "login", "portal", "secure", "api"]
        if finding['type'] == 'subdomain' and any(kw in finding['subdomain'].lower() for kw in keywords):
            return 9
        elif finding['type'] == 'secret':
            return 8
        elif finding['type'] == 'vulnerability' and finding.get('severity') in ['high', 'critical']:
            return 8
        return 5

    def identify_attack_paths(self, target):
        target_node = self.normalize_domain(target)
        critical_assets = [n for n, data in self.graph.nodes(data=True) if data.get('criticality', 0) >= 8]
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
        return sum(self.graph.nodes[n].get('criticality', 0) for n in path)

    def normalize_domain(self, domain):
        return domain.lower().strip()