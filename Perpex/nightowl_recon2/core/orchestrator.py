# core/orchestrator.py - Complete Production-Ready Implementation

import asyncio
import subprocess
import time
import threading
import psutil
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import json

from core.state_manager import StateManager
from core.resource_monitor import ResourceMonitor
from core.workflow_engine import WorkflowEngine
from utils.file_manager import FileManager
from utils.error_handler import ErrorHandler

from tools.subdomain.subfinder import SubfinderScanner
from tools.subdomain.crtsh import CrtShScanner
from tools.subdomain.dnsx import DNSXScanner


class NightOwlOrchestrator:
    def __init__(self, target, mode, output_dir):
        self.target = target
        self.mode = mode
        self.output_dir = Path(output_dir)

        self._lock = threading.RLock()
        self._scan_results = {}
        self._tool_stats = {}
        self._failed_tools = {}
        self._verbose_logs = []

        self.current_phase = 0
        self.scan_start_time = datetime.now()

        self.state_manager = StateManager(self.output_dir)
        self.resource_monitor = ResourceMonitor()
        self.file_manager = FileManager(self.output_dir)
        self.workflow_engine = WorkflowEngine(self.mode)
        self.error_handler = ErrorHandler(self.output_dir)

        self.tools = {}
        self._initialize_tools()

    def log_verbose(self, msg):
        with self._lock:
            self._verbose_logs.append(msg)
            if len(self._verbose_logs) > 300:
                self._verbose_logs.pop(0)

    async def run(self):
        self.resource_monitor.start()
        phases = self.workflow_engine.get_phases()
        for idx, phase in enumerate(phases, start=1):
            self.current_phase = idx
            await self._run_phase(phase)
        self.resource_monitor.stop()
        self._final_summary()

    async def _run_phase(self, phase):
        tasks = [asyncio.create_task(self._run_tool(name)) for name in phase.tools]
        await asyncio.gather(*tasks)

        self.current_phase = 2
        self._merge_and_dedup_subdomains()

        self.current_phase = 3
        self._run_liveness_check()

        self.current_phase = 4
        self.extract_important_subdomains()

        self.current_phase = 5
        self.capture_screenshots()
        self.generate_screenshot_gallery()

    def _initialize_tools(self):
        tool_map = {
            "subfinder": SubfinderScanner,
            "crtsh": CrtShScanner,
            "dnsx": DNSXScanner
        }
        for name, cls in tool_map.items():
            try:
                self.tools[name] = cls(log_fn=self.log_verbose)
            except Exception as e:
                self._failed_tools[name] = str(e)

    async def _run_tool(self, name):
        try:
            tool = self.tools[name]
            t0 = time.time()
            results = await tool.scan(self.target)
            elapsed = round(time.time() - t0, 1)

            f = self.output_dir / f"{name}.txt"
            f.write_text("\n".join(sorted({r['domain'] for r in results})))

            self._scan_results[name] = results
            self._tool_stats[name] = {"time": elapsed, "count": len(results)}
            self.log_verbose(f"[✔] {name} complete: {len(results)} items")
        except Exception as e:
            self._failed_tools[name] = str(e)
            self.log_verbose(f"[✖] {name} error: {e}")

    def _merge_and_dedup_subdomains(self):
        merged = set()
        for fname in ["subfinder.txt", "crtsh.txt", "dnsx.txt"]:
            f = self.output_dir / fname
            if f.exists():
                merged.update(line.strip().lower() for line in f.read_text().splitlines())
        out = self.output_dir / "all_subdomains.txt"
        out.write_text("\n".join(sorted(merged)))
        self.log_verbose(f"[+] Merged {len(merged)} subdomains.")

    def _run_liveness_check(self):
        src = self.output_dir / "all_subdomains.txt"
        livef = self.output_dir / "live.txt"
        deadf = self.output_dir / "dead.txt"

        if not src.exists():
            self.log_verbose("[⚠] No subdomains found.")
            return

        try:
            subprocess.run(
                ["httpx", "-list", str(src), "-silent", "-mc", "200,301,302,403", "-o", str(livef)],
                check=True, capture_output=True, text=True
            )

            def norm(line):
                raw = urlparse(line.strip())
                return raw.hostname if raw.hostname else line.strip()

            all_set = {norm(l) for l in src.read_text().splitlines() if l.strip()}
            live_set = {norm(l) for l in livef.read_text().splitlines() if l.strip()}
            dead_list = sorted(all_set - live_set)

            deadf.write_text("\n".join(dead_list))
            self.log_verbose(f"[httpx] Live: {len(live_set)} / Dead: {len(dead_list)}")

        except Exception as e:
            self.log_verbose(f"[httpx] failed: {e}")

    def extract_important_subdomains(self):
        inp = self.output_dir / "live.txt"
        out = self.output_dir / "important.txt"
        if not inp.exists(): return

        keywords = ["admin", "login", "api", "dashboard", "staging", "upload", "test", "dev"]
        found = [l for l in inp.read_text().splitlines() if any(k in l.lower() for k in keywords)]
        out.write_text("\n".join(sorted(found)))
        self.log_verbose(f"[important] Found {len(found)} important")

    def capture_screenshots(self):
        live = self.output_dir / "live.txt"
        urls_file = self.output_dir / "urls_for_screenshots.txt"
        ss_dir = self.output_dir / "screenshots"
        ss_dir.mkdir(exist_ok=True)

        if not live.exists():
            self.log_verbose("[gowitness] No live.txt — skipping")
            return

        urls = []
        for l in live.read_text().splitlines():
            l = l.strip()
            if not l.startswith("http"):
                l = "http://" + l
            urls.append(l)

        urls_file.write_text("\n".join(urls))

        try:
            subprocess.run([
                "gowitness", "scan", "file",
                "-f", str(urls_file),
                "--screenshot-format", "png",
                "--screenshot-path", str(ss_dir),
                "--timeout", "15"
            ], check=True)

            self.log_verbose(f"[gowitness] Screenshots captured: {len(list(ss_dir.glob('*.png')))}")

        except Exception as e:
            self.log_verbose(f"[gowitness] Failed: {e}")

    def generate_screenshot_gallery(self):
        import json

        ss_dir = self.output_dir / "screenshots"
        gallery_file = self.output_dir / "screenshots.html"
        live_file = self.output_dir / "live.txt"
        fail_file = self.output_dir / "unscreenshoted.txt"
        if not ss_dir.exists():
            return

        screenshots = {str(p.name): p for p in ss_dir.glob("*.png")}
        slides = []
        domains = [l.strip() for l in live_file.read_text().splitlines() if l.strip()]
        failed = []

        for d in domains:
            expected = f"http__{d.replace('.', '_')}.png"
            if expected in screenshots:
                slides.append({"filename": expected, "domain": d})
            else:
                failed.append(d)

        if failed:
            fail_file.write_text("\n".join(failed))
            self.log_verbose(f"[gallery] {len(failed)} domains unscreenshoted")

        html = f"""
        <html>
        <head>
            <title>Screenshot Gallery</title>
            <style>
                html,body {{ background:#111; color:#eee; font-family:sans-serif; margin:0; }}
                #slide-container {{
                    height:100vh; display:flex; flex-direction:column; align-items:center; justify-content:center;
                }}
                img#sshot {{
                    max-width:94vw; max-height:68vh; border:2px solid #333; border-radius:8px;
                    box-shadow:0 2px 16px #000;
                }}
                .caption {{
                    font-size:1.7em; margin-bottom:.5em; font-family:monospace; text-align:center;
                }}
                .nav-btns button {{
                    margin:0 2em; font-size:1em; padding:.5em 2em; background:#234; color:#fff; border:none; border-radius:6px; cursor:pointer;
                }}
                #counter {{ margin-top:.7em; color:#aaa; font-size:1.1em; text-align:center; }}
                #missed-list {{ margin-top:3em; color:#ff6666; }}
                ul {{ margin:1em 0 0 2em; }}
            </style>
        </head>
        <body>
            <div id="slide-container">
                <div class="caption" id="caption"></div>
                <img id="sshot" src="" alt="Screenshot"/>
                <div id="counter"></div>
                <div class="nav-btns">
                    <button onclick="prev()" id="prevbtn">← Prev</button>
                    <button onclick="next()" id="nextbtn">Next →</button>
                </div>
            </div>
            <script>
                let i = 0;
                const slides = {json.dumps(slides)};
                function show(n) {{
                    i = n;
                    if(slides.length < 1) return;
                    document.getElementById('sshot').src = "screenshots/" + slides[i].filename;
                    document.getElementById('caption').innerText = slides[i].domain;
                    document.getElementById('counter').innerText = `Slide ${{i+1}} / ${{slides.length}}`;
                    document.getElementById('prevbtn').disabled = (i === 0);
                    document.getElementById('nextbtn').disabled = (i === slides.length-1);
                }}
                function next() {{ if(i<slides.length-1) show(i+1); }}
                function prev() {{ if(i>0) show(i-1); }}
                document.getElementById('sshot').onclick = next;
                document.addEventListener('keydown', function(e) {{
                    if(e.key==="ArrowRight") next();
                    else if(e.key==="ArrowLeft") prev();
                }});
                window.onload = ()=>{{ show(0); }};
            </script>
            {"<hr><div id='missed-list'><b>❌ Domains with no screenshot:</b><ul>" + "".join(f"<li>{d}</li>" for d in failed) + "</ul></div>" if failed else ""}
        </body>
        </html>
        """
        gallery_file.write_text(html)
        self.log_verbose("[gallery] Updated one-slide-per-domain screenshots.html generated.")

    def _final_summary(self):
        elapsed = round((datetime.now() - self.scan_start_time).total_seconds(), 1)
        self.log_verbose(f"[✔] Final scan complete in {elapsed}s")
        self.generate_report()

    def generate_report(self):
        stats = self.get_scan_statistics()
        md = [
            f"# 🦉 Recon Report: {self.target}",
            f"- Mode: `{self.mode}`",
            f"- Duration: {stats['elapsed_time']}",
            "",
            "## Scan Summary",
            f"- Subdomains: {stats['merged_subdomains']}",
            f"- Live hosts: {stats['live_hosts']}",
            f"- Dead hosts: {stats['dead_hosts']}",
            f"- Important: {stats['important_hosts']}",
            f"- Screenshots: {len(list((self.output_dir / 'screenshots').glob('*.png')))}",
            "- [🖼️ Screenshot Gallery](screenshots.html)"
        ]
        (self.output_dir / "recon_report.md").write_text("\n".join(md))
        self.log_verbose("[report] recon_report.md created.")

    def get_scan_statistics(self):
        return {
            "target": self.target,
            "mode": self.mode,
            "current_phase": self.current_phase,
            "total_phases": 6,
            "completed_tools": len(self._scan_results),
            "failed_tools": len(self._failed_tools),
            "merged_subdomains": self._count("all_subdomains.txt"),
            "live_hosts": self._count("live.txt"),
            "dead_hosts": self._count("dead.txt"),
            "important_hosts": self._count("important.txt"),
            "elapsed_time": f"{(datetime.now() - self.scan_start_time).total_seconds():.1f}s",
            "resource_usage": self.resource_monitor.get_usage(),
        }

    def _count(self, filename):
        path = self.output_dir / filename
        return sum(1 for _ in path.open()) if path.exists() else 0

    @property
    def scan_results(self):
        return self._scan_results

    @property
    def failed_tools(self):
        return self._failed_tools

    @property
    def tool_stats(self):
        return self._tool_stats

    @property
    def verbose_logs(self):
        return self._verbose_logs
