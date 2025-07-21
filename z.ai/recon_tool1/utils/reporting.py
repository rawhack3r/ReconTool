# Add these imports at the TOP
from typing import Set, List, Dict, Any
from datetime import datetime
import jinja2
import os
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

class ReportGenerator:
    def __init__(self):
        try:
            self.template_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader("templates/"),
                autoescape=True
            )
            self.template_env.get_template("report.html.j2")
        except jinja2.TemplateNotFound:
            raise SystemExit("[red]FATAL: Missing report.html.j2 in templates/")

    def generate_report(self, subdomains: Set[str], vulns: List[Dict], live_domains: List[str]):
        try:
            template = self.template_env.get_template("report.html.j2")
            report = template.render(
                subdomains=sorted(subdomains),
                vulns=vulns,
                live_domains=live_domains,
                timestamp=datetime.now().strftime("%Y-%m-%d_%H%M%S"),
                errors=self._format_errors()
            )
            with open(f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "w") as f:
                f.write(report)
            console.print(f"[green]Report saved: report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        except Exception as e:
            raise SystemExit(f"[red]Report generation failed: {str(e)}")

    def _format_errors(self) -> List[str]:
        return [f"Error: {e}" for e in self.results.get("errors", [])]