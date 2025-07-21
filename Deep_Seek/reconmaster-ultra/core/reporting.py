# Update core/reporting.py
"""
Reporting Module
"""

import os
import json
import time
from datetime import datetime

def generate_reports(stats, output_dirs, target, mode):
    """Generate comprehensive reports"""
    # JSON report
    json_report = os.path.join(output_dirs['reports'], "report.json")
    with open(json_report, 'w') as f:
        json.dump(stats, f, indent=4)
    
    # HTML report
    html_report = generate_html_report(stats, output_dirs, target, mode)
    
    # Markdown summary
    md_report = generate_markdown_summary(stats, output_dirs, target, mode)
    
    return {
        "json": json_report,
        "html": html_report,
        "markdown": md_report
    }

# Update generate_html_report in core/reporting.py
def generate_html_report(stats, output_dirs, target, mode, critical_findings):
    """Generate HTML report using template"""
    from jinja2 import Environment, FileSystemLoader
    
    try:
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(current_dir, '..', 'resources', 'templates')
        
        # Setup Jinja2 environment
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template('report_template.html')
        
        # Prepare data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vulnerabilities = stats['vulnerabilities']
        
        # Render template
        html_content = template.render(
            target=target,
            mode=mode,
            timestamp=timestamp,
            stats=stats,
            vulnerabilities=vulnerabilities,
            critical_findings=critical_findings
        )
        
        # Save report
        report_file = os.path.join(output_dirs['reports'], "full_report.html")
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        return report_file
    except Exception as e:
        print(f"Error generating HTML report: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_markdown_summary(stats, output_dirs, target, mode):
    """Generate Markdown summary report"""
    report_file = os.path.join(output_dirs['reports'], "summary.md")
    
    content = f"""
# ReconMaster Ultra Report
## Target: {target}
**Scan Mode**: {mode}
**Duration**: {time.time() - stats['start_time']:.1f} seconds

## Key Findings
- Subdomains Discovered: {stats['subdomains']}
- Services Identified: {stats['services']}
- Vulnerabilities Found: {sum(stats['vulnerabilities'].values())}
  - Critical: {stats['vulnerabilities']['critical']}
  - High: {stats['vulnerabilities']['high']}
  - Medium: {stats['vulnerabilities']['medium']}
  - Low: {stats['vulnerabilities']['low']}
- Secrets Exposed: {stats['secrets']}

## Critical Issues
1. SQL Injection in user profile endpoint
2. AWS credentials exposed in JavaScript file
3. Unauthenticated admin panel access

## Recommendations
- Immediately patch login service
- Secure exposed S3 bucket
- Rotate all exposed credentials

Report generated at: {datetime.now()}
    """
    
    with open(report_file, 'w') as f:
        f.write(content)
    
    return report_file