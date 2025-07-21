from jinja2 import Environment, FileSystemLoader
from core.error_handler import ErrorHandler
import os
import re

class ReportGenerator:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader('config/templates'))

    def generate_report(self, target, results, start_time):
        try:
            os.makedirs(f"output/reports", exist_ok=True)
            sensitive_domains = self.flag_sensitive_domains(results.get('subdomains', []))
            important_paths = self.identify_important_paths(results.get('endpoints', []))
            total_time = time.time() - start_time
            report_data = {
                'target': target,
                'results': results,
                'sensitive_domains': sensitive_domains,
                'important_paths': important_paths,
                'total_time': f"{total_time:.2f} seconds",
                'subdomain_count': len(results.get('subdomains', [])),
                'secret_count': len(results.get('secrets', [])),
                'endpoint_count': len(results.get('endpoints', [])),
                'vuln_count': len(results.get('vulnerabilities', []))
            }
            template = self.env.get_template('report.html.j2')
            output = template.render(**report_data)
            with open(f"output/reports/{target}_report.html", "w") as f:
                f.write(output)
            self.generate_manual_checklist(target, sensitive_domains, important_paths)
        except Exception as e:
            ErrorHandler.log_error(f"Report generation failed: {str(e)}")

    def flag_sensitive_domains(self, subdomains):
        sensitive_keywords = ["admin", "login", "portal", "secure", "api", "dashboard", "auth"]
        return [s for s in subdomains if any(kw in s['subdomain'].lower() for kw in sensitive_keywords)]

    def identify_important_paths(self, endpoints):
        important_keywords = ["admin", "api", "login", "config", "backup", "test", "dev"]
        return [e for e in endpoints if any(kw in e['endpoint'].lower() for kw in important_keywords)]

    def generate_manual_checklist(self, target, sensitive_domains, important_paths):
        checklist = f"""
# Manual Checking Checklist for {target}

- **Verify Sensitive Domains**: Check domains with keywords like "admin" or "api" for exposed panels.
  - Examples: {', '.join([s['subdomain'] for s in sensitive_domains[:5]])}
- **Test Important Paths**: Manually test endpoints with keywords like "admin" or "api" for vulnerabilities like IDOR or XSS.
  - Examples: {', '.join([e['endpoint'] for e in important_paths[:5]])}
- **Review Secrets**: Validate detected secrets (e.g., API keys, emails) for authenticity and access.
- **Check Cloud Assets**: Investigate public cloud resources for misconfigurations.
- **Perform Manual Scans**: Use Burp Suite or manual HTTP requests to explore flagged vulnerabilities.
"""
        with open(f"output/reports/{target}_checklist.md", "w") as f:
            f.write(checklist)