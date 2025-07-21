import os
import yaml
import math

def load_config():
    try:
        from config import settings
        return {
            'SCAN_MODES': settings.SCAN_MODES,
            'WORKFLOWS': settings.WORKFLOWS,
            'TOOLS': settings.TOOLS,
            'CLOUD_PROVIDERS': settings.CLOUD_PROVIDERS,
            'MAX_WORKERS': settings.MAX_WORKERS,
            'CHECKPOINT_INTERVAL': settings.CHECKPOINT_INTERVAL,
            'MAX_CPU': settings.MAX_CPU,
            'MAX_MEMORY': settings.MAX_MEMORY
        }
    except ImportError:
        return {
            'SCAN_MODES': ["light", "deep", "deeper", "custom"],
            'WORKFLOWS': {
                "light": ["Subdomain Discovery", "Information Extraction"],
                "deep": ["Threat Intelligence", "Subdomain Discovery", "Information Extraction", 
                         "API Security Testing", "Vulnerability Scanning"],
                "deeper": ["Threat Intelligence", "Subdomain Discovery", "Information Extraction", 
                           "API Security Testing", "Vulnerability Scanning", "Cloud Infrastructure Scan", 
                           "AI-Powered Analysis", "Attack Surface Mapping", "Phishing Detection", 
                           "Blockchain Analysis"]
            },
            'TOOLS': {
                "subdomain_enum": ["amass", "subfinder", "chaos"],
                "vulnerability": ["nuclei", "zap"]
            },
            'CLOUD_PROVIDERS': ["AWS", "Azure", "GCP"],
            'MAX_WORKERS': 8,
            'CHECKPOINT_INTERVAL': 300,
            'MAX_CPU': 0.8,
            'MAX_MEMORY': 0.8
        }

def entropy(s):
    """Calculate Shannon entropy for a string"""
    if not s:
        return 0
    entropy_val = 0
    for x in range(256):
        p_x = s.count(chr(x)) / len(s)
        if p_x > 0:
            entropy_val += - p_x * math.log2(p_x)
    return entropy_val

def calculate_risk_score(graph):
    """
    Calculate overall risk score for an attack surface graph
    
    :param graph: NetworkX graph object representing attack surface
    :return: Numeric risk score (0-100)
    """
    if len(graph.nodes) == 0:
        return 0
    
    # Calculate weighted risk based on nodes and edges
    node_risks = [data['risk'] for node, data in graph.nodes(data=True)]
    avg_node_risk = sum(node_risks) / len(node_risks)
    
    # Increase risk based on number of critical paths
    critical_nodes = [n for n, d in graph.nodes(data=True) if d['risk'] >= 80]
    
    # Fixed: Added missing parenthesis at the end of min() function
    critical_path_factor = min(1.5, 1 + len(critical_nodes) * 0.1)
    
    # Calculate final risk score
    risk_score = avg_node_risk * critical_path_factor
    return min(100, risk_score)