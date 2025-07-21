import json
import os
import jinja2
from datetime import datetime

REPORT_TEMPLATE = "config/templates/report.html.j2"
OUTPUT_DIR = "outputs/reports"

def generate_html_report(report_data, filename):
    """Generate HTML report from template"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Calculate durations
    start_time = datetime.fromisoformat(report_data['start_time'])
    end_time = datetime.fromisoformat(report_data.get('end_time', datetime.now().isoformat()))
    duration = end_time - start_time
    
    # Prepare data for template
    report_data['duration'] = str(duration)
    report_data['stats'] = report_data.get('stats', {})
    
    # Load template
    template_loader = jinja2.FileSystemLoader(searchpath="./")
    template_env = jinja2.Environment(loader=template_loader)
    
    try:
        template = template_env.get_template(REPORT_TEMPLATE)
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        return None
    
    # Render report
    html = template.render(report_data)
    
    # Save to file
    report_path = os.path.join(OUTPUT_DIR, f"{filename}.html")
    with open(report_path, 'w') as f:
        f.write(html)
    
    return report_path

def generate_text_summary(report_data):
    """Generate text summary of results"""
    summary = [
        f"NightOwl Reconnaissance Report",
        f"Target: {report_data['target']}",
        f"Scan Mode: {report_data['mode']}",
        f"Start Time: {report_data['start_time']}",
        f"End Time: {report_data.get('end_time', 'Incomplete')}",
        f"Duration: {report_data.get('duration', 'N/A')}",
        "",
        "=== Summary ===",
        f"Subdomains Found: {report_data['stats'].get('subdomains', 0)}",
        f"Critical Assets: {report_data['stats'].get('critical_assets', 0)}",
        f"Vulnerabilities Found: {report_data['stats'].get('vulnerabilities', 0)}",
        f"Secrets Found: {report_data['stats'].get('secrets', 0)}",
        "",
        "=== Next Steps ===",
        "1. Review important findings in outputs/important/",
        "2. Validate vulnerabilities in outputs/vulnerabilities/",
        "3. Check manual_testing_checklist.md for critical areas"
    ]
    
    return "\n".join(summary)