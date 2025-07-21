from typing import Set, List
import subprocess
import shlex

class SubdomainScanner:
    def __init__(self, targets: List[str], proxies: List[str]):
        self.targets = targets
        self.proxies = proxies

    def run(self) -> Set[str]:
        results = set()
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(self._subfinder),
                executor.submit(self._amass),
                executor.submit(self._findomain)
            ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.update(result)
                except Exception as e:
                    print(f"[yellow]Subdomain tool error: {str(e)}")
        return results

    def _subfinder(self) -> List[str]:
        return self._run_tool("subfinder -dL {targets} -silent -oJ -".format(targets=",".join(self.targets)))

    def _amass(self) -> List[str]:
        return self._run_tool("amass enum -d {targets} -passive -oJ -".format(targets=",".join(self.targets)))

    def _run_tool(self, cmd: str) -> List[str]:
        try:
            process = subprocess.run(
                shlex.split(cmd),
                capture_output=True,
                text=True,
                timeout=120
            )
            return json.loads(process.stdout).get("subdomains", [])
        except Exception as e:
            return []