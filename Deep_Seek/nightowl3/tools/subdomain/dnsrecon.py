import subprocess
import xml.etree.ElementTree as ET
import os

def run(target, output_dir):
    output_file = os.path.join(output_dir, "dnsrecon.xml")
    cmd = f"dnsrecon -d {target} -t brt -x {output_file}"
    
    try:
        subprocess.run(cmd, shell=True, timeout=900)
        
        # Parse XML results
        if os.path.exists(output_file):
            tree = ET.parse(output_file)
            root = tree.getroot()
            
            subdomains = set()
            for host in root.findall(".//host"):
                hostname = host.get("name")
                if hostname and target in hostname:
                    subdomains.add(hostname)
            
            return list(subdomains)
        return []
    except:
        return []