import os
import json
import jinja2
from datetime import datetime

def generate_html_report(state, target):
    report_data = {
        'target': target,
        'start_time': state.get('start_time'),
        'end_time': state.get('end_time', datetime.now().isoformat()),
        'mode': state.get('mode'),
        'results': state.get('results', {}),
        'errors': state.get('errors', [])
    }
    
    template_loader = jinja2.FileSystemLoader(searchpath="config/templates")
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template("report.html.j2")
    
    html = template.render(report_data)
    
    report_dir = "outputs/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{target}_report.html")
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path

def generate_executive_summary(state):
    summary = [
        f"NightOwl Reconnaissance Report for {state['target']}",
        f"Scan Mode: {state['mode']}",
        f"Start Time: {state['start_time']}",
        f"End Time: {state.get('end_time', 'Incomplete')}",
        "",
        "=== Key Findings ==="
    ]
    
    if 'subdomains' in state['results']:
        count = sum(len(tool_data) for tool_data in state['results']['subdomains'].values())
        summary.append(f"- Discovered {count} subdomains")
    
    if 'vulnerabilities' in state['results']:
        count = sum(len(vulns) for vulns in state['results']['vulnerabilities'].values())
        summary.append(f"- Found {count} vulnerabilities")
    
    if 'phishing_detection' in state['results']:
        count = len(state['results']['phishing_detection'])
        summary.append(f"- Detected {count} potential phishing sites")
    
    summary.append("\n=== Recommendations ===")
    summary.append("- Review critical vulnerabilities immediately")
    summary.append("- Check exposed cloud resources for misconfigurations")
    summary.append("- Investigate potential phishing sites")
    
    report_dir = "outputs/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{state['target']}_summary.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(summary))
    
    return report_path