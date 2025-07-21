from typing import Set, List
import subprocess
import shlex

class ActiveScanner:
    def __init__(self, subdomains: Set[str], proxies: List[str]):
        self.subdomains = subdomains
        self.lived_domains = []
        self.proxies = proxies

    def run(self):
        self._httprobe()
        self._masscan()

    def _httprobe(self):
        cmd = f"httpx -c 200 {' '.join(self.subdomains)}"
        result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
        self.lived_domains = set(line.strip() for line in result.stdout.splitlines() if line.strip())

    def _masscan(self):
        ports = "22,80,443,8000-8100" if self.mode == "default" else "1-65535"
        cmd = f"masscan -iL <(echo {' '.join(self.subdomains)}) -p {ports} --rate 1000"
        subprocess.run(shlex.split(cmd), capture_output=True, text=True)