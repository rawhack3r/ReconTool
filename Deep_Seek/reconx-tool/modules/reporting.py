import os
import json
import datetime
from jinja2 import Environment, FileSystemLoader

class ReportGenerator:
    def __init__(self, results, output_dir, mode, 
                 scan_duration, errors=None):
        self.results = results
        self.output_dir = output_dir
        self.mode = mode
        self.scan_duration = scan_duration
        self.errors = errors or []
        self.template_dir = os.path.join(os.path.dirname(__file__), "config", "templates")
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate(self):
        # Create report directory
        report_dir = os.path.join(self.output_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate reports for each target
        for target, data in self.results.items():
            self._generate_target_report(target, data, report_dir)
        
        # Generate summary report
        summary_path = self._generate_summary_report(report_dir)
        return summary_path
    
    def _generate_target_report(self, target, data, report_dir):
        template = self.env.get_template("target_report.html")
        report_path = os.path.join(report_dir, f"{target}_report.html")
        
        # Prepare data for template
        report_data = {
            "target": target,
            "scan_mode": self.mode,
            "scan_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scan_duration": round(self.scan_duration, 2),
            "subdomain_count": data.get("subdomain_count", 0),
            "vulnerabilities": data.get("vulnerabilities", []),
            "errors": self.errors,
            "data": data
        }
        
        # Render and save report
        html = template.render(report_data)
        with open(report_path, "w") as f:
            f.write(html)
        
        return report_path
    
    def _generate_summary_report(self, report_dir):
        template = self.env.get_template("summary_report.html")
        report_path = os.path.join(report_dir, "summary_report.html")
        
        # Prepare summary data
        summary_data = {
            "target_count": len(self.results),
            "total_subdomains": sum(data.get("subdomain_count", 0) for data in self.results.values()),
            "vulnerability_count": sum(len(data.get("vulnerabilities", [])) for data in self.results.values()),
            "error_count": len(self.errors),
            "scan_mode": self.mode,
            "scan_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scan_duration": round(self.scan_duration, 2),
            "targets": self.results.keys(),
            "errors": self.errors
        }
        
        # Render and save report
        html = template.render(summary_data)
        with open(report_path, "w") as f:
            f.write(html)
        
        return report_path