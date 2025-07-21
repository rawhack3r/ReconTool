import json
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_amass_output(file_path):
    """Parse Amass JSON output"""
    results = {"subdomains": []}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                data = json.loads(line)
                results["subdomains"].append({
                    "domain": data['name'],
                    "source": data['sources'],
                    "resolved": data.get('resolved', False),
                    "resolved_ips": [addr['ip'] for addr in data.get('addresses', [])],
                    "timestamp": data.get('timestamp', str(datetime.now()))
                })
    except Exception as e:
        return {"error": str(e), "raw": open(file_path).read()}
    return results

def parse_nmap_xml(file_path):
    """Parse Nmap XML output"""
    results = {"hosts": []}
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for host in root.findall('host'):
            host_data = {
                "ip": host.find('address').get('addr'),
                "hostnames": [hn.get('name') for hn in host.findall('hostnames/hostname')],
                "ports": []
            }
            
            for port in host.findall('ports/port'):
                port_data = {
                    "port": port.get('portid'),
                    "protocol": port.get('protocol'),
                    "state": port.find('state').get('state'),
                    "service": port.find('service').get('name') if port.find('service') is not None else "unknown",
                    "version": port.find('service').get('version') if port.find('service') is not None else "",
                }
                host_data["ports"].append(port_data)
            
            results["hosts"].append(host_data)
    except Exception as e:
        return {"error": str(e), "raw": open(file_path).read()}
    return results

def parse_findomain_output(file_path):
    """Parse Findomain text output"""
    results = {"subdomains": []}
    try:
        with open(file_path, 'r') as f:
            for domain in f:
                domain = domain.strip()
                if domain:
                    results["subdomains"].append({
                        "domain": domain,
                        "source": "findomain",
                        "resolved": False
                    })
    except Exception as e:
        return {"error": str(e), "raw": open(file_path).read()}
    return results

def normalize_domain(domain):
    """Standardize domain formatting"""
    domain = domain.lower().strip()
    if domain.startswith("http://"):
        domain = domain[7:]
    if domain.startswith("https://"):
        domain = domain[8:]
    if domain.startswith("*."):
        domain = domain[2:]
    return domain.split("/")[0]  # Remove paths

def is_cloud_domain(domain):
    """Check if domain belongs to a cloud provider"""
    cloud_domains = [
        ".aws.", ".amazonaws.com",
        ".azure.", ".azurewebsites.net",
        ".cloud.google.com", ".googleapis.com",
        ".cloudapp.net", ".cloudapp.azure.com"
    ]
    return any(cd in domain for cd in cloud_domains)