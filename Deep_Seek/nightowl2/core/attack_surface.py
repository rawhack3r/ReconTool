import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from pyvis.network import Network
from core.utils import calculate_risk_score  # Fixed import

class AttackSurfaceMapper:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.risk_scores = {}
    
    def add_node(self, node, node_type, attributes=None):
        attributes = attributes or {}
        risk = attributes.get('risk_score', 30)
        self.graph.add_node(node, node_type=node_type, risk=risk, **attributes)
        self.risk_scores[node] = risk
    
    def add_edge(self, source, target, edge_type, weight=1):
        self.graph.add_edge(source, target, edge_type=edge_type, weight=weight)
    
    def generate_interactive_map(self, target):
        """Generate interactive HTML visualization"""
        net = Network(height="750px", width="100%", directed=True)
        
        # Add nodes
        for node, data in self.graph.nodes(data=True):
            risk = data['risk']
            title = f"{node}\nType: {data['node_type']}\nRisk: {risk}%"
            net.add_node(
                node, 
                label=node,
                title=title,
                color=self._get_risk_color(risk),
                size=10 + (risk / 2)
            )
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            net.add_edge(
                source, 
                target,
                title=data['edge_type'],
                width=data.get('weight', 1)
            )
        
        # Save visualization
        map_dir = "outputs/attack_surface"
        os.makedirs(map_dir, exist_ok=True)
        map_path = os.path.join(map_dir, f"{target}_attack_surface.html")
        net.save_graph(map_path)
        
        return map_path
    
    def generate_risk_report(self, target):
        """Generate risk assessment report"""
        critical_nodes = [n for n, d in self.graph.nodes(data=True) if d['risk'] >= 80]
        critical_paths = []
        
        for node in critical_nodes:
            try:
                # Find paths to high-value targets
                paths = list(nx.all_simple_paths(
                    self.graph, 
                    source=node, 
                    target=target,
                    cutoff=3
                ))
                critical_paths.extend(paths)
            except:
                continue
        
        # Create directory if not exists
        map_dir = "outputs/attack_surface"
        os.makedirs(map_dir, exist_ok=True)
        
        report = {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "critical_node_count": len(critical_nodes),
            "exposure_score": calculate_risk_score(self.graph),  # Using fixed function
            "critical_paths": critical_paths,
            "recommendations": self._generate_recommendations()
        }
        
        report_path = os.path.join(map_dir, f"{target}_risk_report.json")
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report_path
    
    def _generate_recommendations(self):
        recs = []
        for node, data in self.graph.nodes(data=True):
            if data['risk'] > 70:
                recs.append(f"Harden security for {node} ({data['node_type']})")
        
        for source, target, data in self.graph.edges(data=True):
            if data['weight'] > 5:  # High connectivity
                recs.append(f"Review connection between {source} and {target}")
        
        return recs
    
    def _get_risk_color(self, risk_score):
        if risk_score > 80: return '#ff0000'  # Red
        if risk_score > 60: return '#ff6600'  # Orange
        if risk_score > 40: return '#ffff00'  # Yellow
        return '#00ff00'  # Green