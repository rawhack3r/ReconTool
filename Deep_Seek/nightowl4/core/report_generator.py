import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def generate_html_report(target, output_dir, state):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report.html.j2')
    
    report_data = {
        "target": target,
        "start_time": state.get("start_time"),
        "end_time": datetime.now().isoformat(),
        "subdomains": state.get("subdomains", []),
        "live_urls": state.get("live_urls", []),
        "vulns": state.get("vulns", {}),
        "info": state.get("info", {}),
        "network": state.get("network", {}),
        "mobile": state.get("mobile", {})
    }
    
    html = template.render(report_data)
    report_path = f"{output_dir}/reports/report.html"
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path

def generate_pdf_report(target, output_dir):
    html_path = f"{output_dir}/reports/report.html"
    pdf_path = f"{output_dir}/reports/report.pdf"
    HTML(html_path).write_pdf(pdf_path)
    return pdf_path