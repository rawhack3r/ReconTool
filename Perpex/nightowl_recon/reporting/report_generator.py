from pathlib import Path
import json
from .templates.html_template import render_html_report
from .templates.json_template import render_json_report

class ReportGenerator:
    def __init__(self, output_dir):
        self.report_dir = Path(output_dir) / "reports"
        self.report_dir.mkdir(exist_ok=True)

    async def generate_html_report(self, scan_results, summary_stats):
        report_path = self.report_dir / "summary.html"
        html_content = render_html_report(scan_results, summary_stats)
        with open(report_path, "w") as f:
            f.write(html_content)

    async def generate_json_report(self, scan_results, summary_stats):
        report_path = self.report_dir / "results.json"
        obj = {
            "summary": summary_stats,
            "tools": {k: v.__dict__ for k, v in scan_results.items()}
        }
        with open(report_path, "w") as f:
            json.dump(obj, f, indent=2)

    async def generate_csv_report(self, scan_results, summary_stats):
        report_path = self.report_dir / "findings.csv"
        # Simple CSV: tool, status, results_count, errors
        with open(report_path, "w") as f:
            f.write("tool,status,results_count,errors\n")
            for tool, res in scan_results.items():
                errs = ";".join(res.errors) if res.errors else ""
                f.write(f"{tool},{res.status},{len(res.results)},{errs}\n")
