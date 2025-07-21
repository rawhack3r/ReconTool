from typing import List, Dict
import subprocess
import json
import os
import shutil
import tempfile

class VulnScanner:
    def __init__(self, domains: List[str]):
        self.domains = domains
        self.nuclei_path = shutil.which("nuclei")
        self.template_path = os.path.expanduser("~/nuclei-templates/cves/")
        self._validate_nuclei()

    def _validate_nuclei(self):
        if not self.nuclei_path:
            raise SystemExit("[red]FATAL: Nuclei not installed!")
        if not os.path.exists(self.template_path):
            raise SystemExit(f"[red]FATAL: Nuclei templates missing at {self.template_path}")

    def run(self) -> List[Dict]:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
                temp_file.write("\n".join(self.domains).encode())
                temp_file.close()

                result = subprocess.run(
                    shlex.split(f"nuclei -l {temp_file.name} -t {self.template_path} -oJ -"),
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode != 0:
                    raise RuntimeError(f"Nuclei exited with code {result.returncode}")

                os.remove(temp_file.name)
                return json.loads(result.stdout)

        except Exception as e:
            raise SystemExit(f"[red]Vuln scan failed: {str(e)}")