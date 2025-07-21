from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os
import json
import datetime

class ReportGenerator:
    def __init__(self):
        try:
            self.template_env = Environment(
                loader=FileSystemLoader("templates/"),
                autoescape=True
            )
            self.template_env.get_template("report.html.j2")
        except TemplateNotFound:
            raise SystemExit("[red]FATAL: Missing report.html.j2 in templates/")

    def generate_report(self, subdomains: Set[str], vulns: List[Dict], live_domains: List[str]):
        try:
            template = self.template_env.get_template("report.html.j2")
            report = template.render(
                subdomains=sorted(subdomains),
                vulns=vulns,
                live_domains=live_domains,
                timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S"),
                errors=self._format_errors()
            )
            with open(f"reports/report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "w") as f:
                f.write(report)
            console.print(f"[green]Report saved: reports/report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        except Exception as e:
            raise SystemExit(f"[red]Report generation failed: {str(e)}")

    def _format_errors(self) -> List[str]:
        return [f"Error: {e}" for e in self.results.get("errors", [])]