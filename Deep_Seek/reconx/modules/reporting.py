import os
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from core.error_handler import ErrorHandler

class ReportGenerator:
    def __init__(self, results, output_dir, mode, scan_duration, errors=None):
        self.results = results
        self.output_dir = output_dir
        self.mode = mode
        self.scan_duration = scan_duration
        self.errors = errors or []
        self.error_handler = ErrorHandler(output_dir)
        self.template_dir = os.path.join(os.path.dirname(__file__), "../config/templates")
        
    def generate(self):
        try:
            # Create report directory
            report_dir = os.path.join(self.output_dir, "reports")
            create_directory(report_dir)
            
            # Generate reports
            summary_path = self._generate_summary_report(report_dir)
            for target in self.results:
                self._generate_target_report(target, report_dir)
                
            return summary_path
        except Exception as e:
            return self.error_handler.handle_exception(e, "reporting")

    def _generate_summary_report(self, report_dir):
        try:
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template("summary_report.html")
            output_path = os.path.join(report_dir, "summary_report.html")
            
            # Prepare data
            total_subdomains = sum(data.get('subdomain_count', 0) for data in self.results.values())
            total_vulns = sum(len(data.get('vulnerabilities', [])) for data in self.results.values())
            
            with open(output_path, 'w') as f:
                f.write(template.render(
                    results=self.results,
                    scan_mode=self.mode,
                    scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    scan_duration=round(self.scan_duration, 2),
                    total_subdomains=total_subdomains,
                    total_vulns=total_vulns,
                    errors=self.errors
                ))
            return output_path
        except Exception as e:
            self.error_handler.log_error(e, "reporting", "summary")
            return None

    def _generate_target_report(self, target, report_dir):
        try:
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template("target_report.html")
            output_path = os.path.join(report_dir, f"{target}_report.html")
            
            with open(output_path, 'w') as f:
                f.write(template.render(
                    target=target,
                    data=self.results[target],
                    scan_mode=self.mode,
                    scan_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            return output_path
        except Exception as e:
            self.error_handler.log_error(e, "reporting", target)
            return None