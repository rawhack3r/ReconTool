import os
import json
import jinja2
from datetime import datetime
from core.utils import Utils

def generate_html_report(target, output_dir, report_path):
    # Gather all results
    results = {
        "subdomains": {"count": 0, "file": f"{output_dir}/subdomains/all.txt"},
        "live_hosts": {"count": 0, "file": f"{output_dir}/live_hosts/alive.txt"},
        "important_domains": {"file": f"{output_dir}/live_hosts/important.txt"},
        "vulns": [],
        "secrets": {"file": f"{output_dir}/info/secrets.txt"},
        "credentials": {"file": f"{output_dir}/info/credentials.txt"}
    }
    
    # Collect data
    if os.path.exists(results["subdomains"]["file"]):
        with open(results["subdomains"]["file"], "r") as f:
            results["subdomains"]["count"] = len(f.readlines())
    
    if os.path.exists(results["live_hosts"]["file"]):
        with open(results["live_hosts"]["file"], "r") as f:
            results["live_hosts"]["count"] = len(f.readlines())
    
    if os.path.exists(results["important_domains"]["file"]):
        with open(results["important_domains"]["file"], "r") as f:
            results["important_domains"]["list"] = f.read().splitlines()
    
    # Load vulnerabilities
    vuln_dir = f"{output_dir}/vulns"
    if os.path.exists(vuln_dir):
        for file in os.listdir(vuln_dir):
            if file.endswith(".json"):
                with open(os.path.join(vuln_dir, file), "r") as f:
                    try:
                        results["vulns"].extend(json.load(f))
                    except:
                        pass
    
    # Load secrets and credentials
    utils = Utils()
    if os.path.exists(results["secrets"]["file"]):
        with open(results["secrets"]["file"], "r") as f:
            results["secrets"]["list"] = [{"type": "Secret", "value": line.strip()} for line in f]
    
    if os.path.exists(results["credentials"]["file"]):
        with open(results["credentials"]["file"], "r") as f:
            results["credentials"]["list"] = [{"type": "Credential", "value": line.strip()} for line in f]
    
    # Calculate duration
    start_time = datetime.strptime(self.state["start_time"], "%Y-%m-%dT%H:%M:%S.%f")
    end_time = datetime.now()
    duration = str(end_time - start_time)
    
    # Setup Jinja2 environment
    template_loader = jinja2.FileSystemLoader(searchpath="templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("report.html.j2")
    
    # Render and save report
    html = template.render(
        target=target,
        date=datetime.now().strftime("%Y-%m-%d"),
        results=results,
        start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
        duration=duration
    )
    
    report_dir = os.path.dirname(report_path)
    os.makedirs(report_dir, exist_ok=True)
    
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path