import json
import os
import jinja2
from datetime import datetime

def generate_html_report(state, filename):
    """Generate comprehensive HTML report"""
    # Prepare report data
    report_data = {
        'target': state['target'],
        'mode': state['mode'],
        'start_time': state['start_time'],
        'end_time': state.get('end_time', datetime.now().isoformat()),
        'duration': state.get('duration', ''),
        'results': state['results'],
        'errors': state.get('errors', []),
        'ai_insights': state.get('results', {}).get('ai_insights', {})
    }
    
    # Setup template environment
    template_loader = jinja2.FileSystemLoader(searchpath="config/templates")
    template_env = jinja2.Environment(loader=template_loader)
    
    # Load template
    template = template_env.get_template("report.html.j2")
    
    # Render report
    html = template.render(report_data)
    
    # Save to file
    report_dir = "outputs/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{filename}.html")
    with open(report_path, "w") as f:
        f.write(html)
    
    return report_path

def generate_executive_summary(state):
    """Generate executive summary text report"""
    summary = [
        f"NightOwl Reconnaissance Report - {state['target']}",
        f"Scan Mode: {state['mode']}",
        f"Start Time: {state['start_time']}",
        f"End Time: {state.get('end_time', 'Incomplete')}",
        f"Duration: {state.get('duration', 'N/A')}",
        "",
        "=== Key Findings ===",
        f"- Subdomains Discovered: {len(state['results'].get('subdomains', {}))}",
        f"- Critical Vulnerabilities: {len(state['results'].get('vulnerabilities', {}).get('critical', []))}",
        f"- Sensitive Data Points: {sum(len(v) for k,v in state['results'].get('information', {}).items() if 'secret' in k)}",
        "",
        "=== AI Insights ==="
    ]
    
    # Add AI insights
    ai_insights = state.get('results', {}).get('ai_insights', {})
    for insight_type, content in ai_insights.items():
        summary.append(f"- {insight_type.upper()}:")
        summary.extend([f"  {line}" for line in content.split('\n')])
    
    # Add recommendations
    summary.extend([
        "",
        "=== Recommendations ===",
        "1. Immediately address critical vulnerabilities",
        "2. Review exposed cloud resources",
        "3. Rotate any exposed credentials",
        "4. Implement WAF rules for identified attack patterns"
    ])
    
    # Save to file
    report_dir = "outputs/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f"{state['target']}_summary.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(summary))
    
    return report_path