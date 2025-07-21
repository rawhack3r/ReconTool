import json
from pathlib import Path

class FileManager:
    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    async def save_tool_results(self, tool, results):
        d = self.output_dir / "scans"
        d.mkdir(exist_ok=True)
        with open(d / f"{tool}.json", "w") as f:
            json.dump(results, f, indent=2)

    async def save_combined_results(self, name, items):
        with open(self.output_dir / "scans" / f"{name}_all.txt", "w") as f:
            for item in sorted(set(items)):
                f.write(f"{item}\n")

    async def save_important_info(self, info):
        imp_dir = self.output_dir / "important"
        imp_dir.mkdir(exist_ok=True)
        for k, v in info.items():
            if isinstance(v, set) or isinstance(v, list):
                with open(imp_dir / f"{k}.txt", "w") as f:
                    for item in v:
                        f.write(f"{item}\n")

    async def save_vulnerabilities_by_severity(self, vulns_by_sev):
        vuln_dir = self.output_dir / "vulnerabilities"
        vuln_dir.mkdir(exist_ok=True)
        for sev, vulns in vulns_by_sev.items():
            with open(vuln_dir / f"{sev}.json", "w") as f:
                json.dump(vulns, f, indent=2)
