import subprocess
import xml.etree.ElementTree as ET
from core.error_handler import ErrorHandler

def run_dnsrecon(target):
    """Run DNSRecon for subdomain enumeration"""
    try:
        output_file = f"dnsrecon_{target}.xml"
        command = f"dnsrecon -d {target} -t brt -x {output_file}"
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=900  # 15 minutes
        )
        
        if result.returncode != 0:
            return {
                "tool": "dnsrecon",
                "status": "error",
                "message": result.stderr
            }
        
        # Parse XML results
        tree = ET.parse(output_file)
        root = tree.getroot()
        
        subdomains = set()
        for host in root.findall(".//host"):
            hostname = host.get("name")
            if hostname and target in hostname:
                subdomains.add(hostname)
        
        return {
            "tool": "dnsrecon",
            "status": "success",
            "data": list(subdomains)
        }
    except Exception as e:
        return {
            "tool": "dnsrecon",
            "status": "error",
            "message": str(e)
        }