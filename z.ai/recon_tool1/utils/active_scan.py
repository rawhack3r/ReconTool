# Full corrected file
from typing import Set, List
import subprocess
import shlex
from typing import Set, List
from typing_extensions import Literal

class ActiveScanner:
    def __init__(self, subdomains: Set[str], proxies: List[str]):
        self.subdomains = subdomains
        self.lived_domains: List[str] = []
        self.proxies = proxies
        self.errors: List[str] = []

    def run(self):
        self._httprobe()
        self._masscan()

    def _httprobe(self):
        cmd = f"httprobe -c 50 {' '.join(self.subdomains)}"
        result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
        self.lived_domains = set(line.strip() for line in result.stdout.splitlines() if line.strip())

    def _masscan(self):
        cmd = f"masscan -iL <(echo {' '.join(self.subdomains)}) -p 1-65535 --rate 1000"
        subprocess.run(shlex.split(cmd), capture_output=True, text=True)