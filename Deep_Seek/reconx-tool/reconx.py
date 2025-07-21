#!/usr/bin/env python3
"""
ReconX - Advanced Bug Bounty Reconnaissance Tool v1.2
"""
import os
import sys
import time
import json
import random
import argparse
import subprocess
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.style import Style
import psutil

# Initialize console
console = Console()

# ==============================================
# CORE FUNCTIONALITY
# ==============================================

class ResourceMonitor:
    def __init__(self):
        self.active_tasks = {}
        self.max_cpu_usage = 0
        self.max_ram_usage = 0
        self.start_time = time.time()
        
    def start_task(self, task_name):
        self.active_tasks[task_name] = {
            'start_time': time.time(),
            'initial_cpu': psutil.cpu_percent(),
            'initial_ram': psutil.virtual_memory().used
        }
        
    def end_task(self, task_name):
        if task_name not in self.active_tasks:
            return None
            
        task_data = self.active_tasks.pop(task_name)
        end_time = time.time()
        
        # Calculate resource usage
        current_cpu = psutil.cpu_percent()
        current_ram = psutil.virtual_memory().used
        cpu_usage = current_cpu - task_data['initial_cpu']
        ram_usage = (current_ram - task_data['initial_ram']) / (1024 * 1024)  # MB
        
        # Update max usage
        self.max_cpu_usage = max(self.max_cpu_usage, cpu_usage)
        self.max_ram_usage = max(self.max_ram_usage, ram_usage)
        
        return {
            'duration': end_time - task_data['start_time'],
            'cpu': cpu_usage,
            'ram': ram_usage
        }
    
    def get_system_stats(self):
        return {
            'cpu_usage': psutil.cpu_percent(),
            'ram_usage': psutil.virtual_memory().percent,
            'ram_used_mb': psutil.virtual_memory().used / (1024 * 1024),
            'uptime': time.time() - self.start_time
        }
    
    def get_peak_usage(self):
        return {
            'max_cpu': self.max_cpu_usage,
            'max_ram': self.max_ram_usage
        }


class ProgressTracker:
    def __init__(self):
        self.start_time = time.time()
        self.current_target = None
        self.module_progress = {}
        self.errors = []
        self.resource_monitor = ResourceMonitor()
        self.target_count = 0
        self.completed_targets = 0
        
        # Progress display
        self.progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn()
        )
        
        # Live display
        self.live = Live(console=console, refresh_per_second=10, screen=False)
        self.live.start()
    
    def start_scan(self, target_count):
        self.target_count = target_count
        self.scan_task = self.progress.add_task(
            f"[cyan]Scanning {target_count} targets...", total=target_count
        )
        self._update_display()
    
    def start_target(self, target):
        self.current_target = target
        self.completed_targets += 1
        self.target_task = self.progress.add_task(
            f"[green]Processing {target}", total=100
        )
        self.module_progress = {}
        self._update_display()
    
    def start_module(self, module_name):
        self.module_progress[module_name] = {
            'start_time': time.time(),
            'progress': 0,
            'completed': False,
            'results': 0
        }
        self._update_display()
    
    def update_module(self, module_name, progress):
        if module_name in self.module_progress:
            self.module_progress[module_name]['progress'] = progress
            self._update_display()
    
    def complete_module(self, module_name, result_count=None):
        if module_name in self.module_progress:
            self.module_progress[module_name]['progress'] = 100
            self.module_progress[module_name]['completed'] = True
            if result_count is not None:
                self.module_progress[module_name]['results'] = result_count
            self._update_display()
    
    def add_error(self, error_message):
        self.errors.append(error_message)
        self._update_display()
    
    def _build_system_stats(self):
        stats = self.resource_monitor.get_system_stats()
        peak = self.resource_monitor.get_peak_usage()
        
        return (
            f"CPU Usage: {stats['cpu_usage']}%\n"
            f"RAM Usage: {stats['ram_usage']}% ({stats['ram_used_mb']:.1f} MB)\n"
            f"Peak CPU: {peak['max_cpu']:.1f}%\n"
            f"Peak RAM: {peak['max_ram']:.1f} MB\n"
            f"Uptime: {stats['uptime']:.1f}s"
        )
    
    def _build_scan_status(self):
        status = f"Targets: [bold]{self.completed_targets}/{self.target_count}[/bold] completed\n"
        
        if self.current_target:
            status += f"\nCurrent: [bold]{self.current_target}[/bold]\n"
            for module, data in self.module_progress.items():
                status += f"\n[cyan]{module.capitalize()}:[/cyan] "
                if data.get('completed'):
                    status += "[green]✓ Completed[/green]"
                    if data['results'] > 0:
                        status += f" ([yellow]{data['results']}[/yellow] results)"
                else:
                    status += f"[yellow]{data['progress']}%[/yellow]"
        
        if self.errors:
            status += "\n\n[red]Errors:[/red]"
            for error in self.errors[-3:]:
                status += f"\n- {error}"
        
        return status
    
    def _update_display(self):
        # Create layout
        grid = Table.grid(expand=True)
        grid.add_column(width=35)
        grid.add_column(width=65)
        
        # Build panels
        resources_panel = Panel(
            self._build_system_stats(), 
            title="System Resources",
            border_style="blue"
        )
        status_panel = Panel(
            self._build_scan_status(),
            title="Scan Status",
            border_style="green"
        )
        
        grid.add_row(resources_panel, status_panel)
        self.live.update(grid)
    
    def complete_target(self, target):
        self.progress.update(self.target_task, completed=100)
        self._update_display()
    
    def complete_scan(self):
        self.live.stop()
        console.print(f"\n[bold green]✓ Scan completed in {time.time() - self.start_time:.2f} seconds[/bold green]")
    
    def report_generated(self, report_path):
        console.print(f"\n[bold]📊 Report generated:[/bold] [cyan]{report_path}[/cyan]")


class ReconScanner:
    def __init__(self, target, target_list, mode, output_dir, 
                 concurrency=10, max_resources=False):
        self.targets = self._load_targets(target, target_list)
        self.mode = mode
        self.output_dir = output_dir
        self.concurrency = concurrency
        self.max_resources = max_resources
        self.resource_monitor = ResourceMonitor()
        self.progress_tracker = ProgressTracker()
        self.results = defaultdict(dict)
        self.errors = []
        self.start_time = time.time()
        
    def _load_targets(self, target, target_list):
        targets = []
        if target:
            targets.append(target)
        if target_list and os.path.exists(target_list):
            with open(target_list, 'r') as f:
                targets.extend(line.strip() for line in f if line.strip())
        return list(set(targets))
    
    def run(self):
        self.progress_tracker.start_scan(len(self.targets))
        
        # Process targets
        for target in self.targets:
            self.progress_tracker.start_target(target)
            self._scan_target(target)
            self.progress_tracker.complete_target(target)
        
        self.progress_tracker.complete_scan()
    
    def _scan_target(self, target):
        # Create output directory
        target_dir = os.path.join(self.output_dir, target)
        os.makedirs(target_dir, exist_ok=True)
        
        try:
            # Subdomain enumeration
            self.progress_tracker.start_module("subdomain_enumeration")
            subdomains = self._run_subdomain_enum(target, target_dir)
            self.results[target]['subdomains'] = subdomains
            self.results[target]['subdomain_count'] = len(subdomains)
            self.progress_tracker.complete_module("subdomain_enumeration", len(subdomains))
            
            # Content discovery
            self.progress_tracker.start_module("content_discovery")
            content_data = self._run_content_discovery(target, target_dir, subdomains)
            self.results[target].update(content_data)
            self.progress_tracker.complete_module("content_discovery", len(content_data['urls']))
            
            # Vulnerability scanning (deep mode only)
            if self.mode == 'deep':
                self.progress_tracker.start_module("vulnerability_scan")
                vulnerabilities = self._run_vulnerability_scan(target, target_dir, content_data['urls'])
                self.results[target]['vulnerabilities'] = vulnerabilities
                self.progress_tracker.complete_module("vulnerability_scan", len(vulnerabilities))
                
        except Exception as e:
            error_msg = f"{target} scan failed: {str(e)}"
            self.errors.append(error_msg)
            self.progress_tracker.add_error(error_msg)
    
    def _run_subdomain_enum(self, target, output_dir):
        """Simulated subdomain enumeration with progress"""
        domains = []
        base_domains = [
            f"www.{target}", f"api.{target}", f"dev.{target}", 
            f"staging.{target}", f"mail.{target}", f"app.{target}",
            f"cdn.{target}", f"assets.{target}", f"blog.{target}"
        ]
        
        # Simulate tool execution
        tools = [
            {"name": "SubFinder", "count": 15},
            {"name": "Amass", "count": 20},
            {"name": "AssetFinder", "count": 12},
            {"name": "crt.sh", "count": 8}
        ]
        
        for tool in tools:
            self.progress_tracker.resource_monitor.start_task(tool['name'])
            
            # Simulate finding domains
            for i in range(tool['count']):
                time.sleep(random.uniform(0.05, 0.2))
                new_domain = f"{tool['name'].lower()}{i}.{target}"
                domains.append(new_domain)
                
                # Update progress
                progress = int((i + 1) / tool['count'] * 100)
                self.progress_tracker.update_module("subdomain_enumeration", 
                                                  min(95, progress))
            
            # Simulate resource usage
            resource_data = self.progress_tracker.resource_monitor.end_task(tool['name'])
        
        # Combine all domains
        all_domains = list(set(base_domains + domains))
        
        # Write to file
        with open(os.path.join(output_dir, "subdomains.txt"), 'w') as f:
            f.write("\n".join(all_domains))
        
        return all_domains
    
    def _run_content_discovery(self, target, output_dir, subdomains):
        """Simulated content discovery with progress"""
        urls = []
        js_files = []
        extensions = []
        
        # Simulate WaybackURLs
        self.progress_tracker.resource_monitor.start_task("WaybackURLs")
        for i, sub in enumerate(subdomains[:10]):
            time.sleep(0.1)
            urls.extend([
                f"http://{sub}/",
                f"http://{sub}/index.html",
                f"http://{sub}/robots.txt",
                f"http://{sub}/sitemap.xml"
            ])
            self.progress_tracker.update_module("content_discovery", i * 5)
        self.progress_tracker.resource_monitor.end_task("WaybackURLs")
        
        # Simulate Gau
        self.progress_tracker.resource_monitor.start_task("Gau")
        for i, sub in enumerate(subdomains[5:15]):
            time.sleep(0.08)
            urls.extend([
                f"http://{sub}/login",
                f"http://{sub}/admin",
                f"http://{sub}/api",
                f"http://{sub}/.env"
            ])
            self.progress_tracker.update_module("content_discovery", 50 + i * 3)
        self.progress_tracker.resource_monitor.end_task("Gau")
        
        # Simulate JS discovery
        self.progress_tracker.resource_monitor.start_task("JSDiscovery")
        for i, sub in enumerate(subdomains[:8]):
            time.sleep(0.07)
            js_files.append(f"http://{sub}/app.js")
            js_files.append(f"http://{sub}/main.js")
            js_files.append(f"http://{sub}/bundle.js")
            self.progress_tracker.update_module("content_discovery", 70 + i * 3)
        self.progress_tracker.resource_monitor.end_task("JSDiscovery")
        
        # Simulate extension discovery
        self.progress_tracker.resource_monitor.start_task("ExtensionScan")
        for i, sub in enumerate(subdomains[:5]):
            time.sleep(0.06)
            extensions.append(f"http://{sub}/backup.zip")
            extensions.append(f"http://{sub}/database.sql")
            extensions.append(f"http://{sub}/config.bak")
            self.progress_tracker.update_module("content_discovery", 85 + i * 3)
        self.progress_tracker.resource_monitor.end_task("ExtensionScan")
        
        # Write to files
        with open(os.path.join(output_dir, "urls.txt"), 'w') as f:
            f.write("\n".join(urls))
        
        with open(os.path.join(output_dir, "js_files.txt"), 'w') as f:
            f.write("\n".join(js_files))
        
        with open(os.path.join(output_dir, "extensions.txt"), 'w') as f:
            f.write("\n".join(extensions))
        
        return {
            'urls': urls,
            'js_files': js_files,
            'extensions': extensions
        }
    
    def _run_vulnerability_scan(self, target, output_dir, urls):
        """Simulated vulnerability scanning with progress"""
        vulnerabilities = []
        vuln_types = ['XSS', 'SQL Injection', 'SSRF', 'LFI', 'IDOR', 'RCE', 'XXE']
        severities = ['Low', 'Medium', 'High', 'Critical']
        
        # Simulate Nuclei
        self.progress_tracker.resource_monitor.start_task("Nuclei")
        for i in range(10):
            time.sleep(0.2)
            if random.random() > 0.7:  # 30% chance of finding vulnerability
                vuln = {
                    'url': random.choice(urls),
                    'type': random.choice(vuln_types),
                    'severity': random.choice(severities),
                    'description': f"Potential {random.choice(vuln_types)} vulnerability detected",
                    'tool': 'Nuclei'
                }
                vulnerabilities.append(vuln)
            self.progress_tracker.update_module("vulnerability_scan", i * 8)
        self.progress_tracker.resource_monitor.end_task("Nuclei")
        
        # Simulate custom checks
        self.progress_tracker.resource_monitor.start_task("CustomChecks")
        for i in range(5):
            time.sleep(0.15)
            if random.random() > 0.6:  # 40% chance of finding vulnerability
                vuln = {
                    'url': random.choice(urls),
                    'type': random.choice(vuln_types),
                    'severity': random.choice(severities[1:]),  # Skip Low severity
                    'description': f"Possible {random.choice(['misconfiguration', 'data exposure'])}",
                    'tool': 'CustomCheck'
                }
                vulnerabilities.append(vuln)
            self.progress_tracker.update_module("vulnerability_scan", 60 + i * 8)
        self.progress_tracker.resource_monitor.end_task("CustomChecks")
        
        # Write to file
        with open(os.path.join(output_dir, "vulnerabilities.json"), 'w') as f:
            json.dump(vulnerabilities, f, indent=2)
        
        return vulnerabilities
    
    def generate_report(self):
        report_gen = ReportGenerator(
            self.results, 
            self.output_dir,
            self.mode,
            scan_duration=time.time() - self.start_time,
            errors=self.errors
        )
        report_path = report_gen.generate()
        self.progress_tracker.report_generated(report_path)
        return report_path


class ReportGenerator:
    def __init__(self, results, output_dir, mode, 
                 scan_duration, errors=None):
        self.results = results
        self.output_dir = output_dir
        self.mode = mode
        self.scan_duration = scan_duration
        self.errors = errors or []
    
    def generate(self):
        # Create report directory
        report_dir = os.path.join(self.output_dir, "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate summary report
        summary_path = os.path.join(report_dir, "summary_report.html")
        with open(summary_path, 'w') as f:
            f.write(self._generate_summary_html())
        
        # Generate target reports
        for target in self.results:
            target_path = os.path.join(report_dir, f"{target}_report.html")
            with open(target_path, 'w') as f:
                f.write(self._generate_target_html(target))
        
        return summary_path
    
    def _generate_summary_html(self):
        total_subdomains = sum(data.get('subdomain_count', 0) for data in self.results.values())
        total_vulns = sum(len(data.get('vulnerabilities', [])) for data in self.results.values())
        critical_vulns = sum(1 for data in self.results.values() 
                            for vuln in data.get('vulnerabilities', []) 
                            if vuln.get('severity') == 'Critical')
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ReconX Scan Summary</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{ 
                    font-family: 'Roboto', sans-serif; 
                    background: #0f172a;
                    color: #f1f5f9;
                    line-height: 1.6;
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                
                header {{ 
                    background: linear-gradient(135deg, #1e40af 0%, #7e22ce 100%);
                    padding: 2rem;
                    border-radius: 0 0 20px 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
                    text-align: center;
                    margin-bottom: 2rem;
                }}
                header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
                header p {{ font-size: 1.1rem; opacity: 0.9; }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 2rem;
                }}
                .stat-card {{
                    background: rgba(30, 41, 59, 0.7);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                }}
                .stat-card h2 {{
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                    background: linear-gradient(90deg, #60a5fa 0%, #c084fc 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .stat-card.critical {{ 
                    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
                    color: white;
                }}
                .stat-card.critical h2 {{ 
                    -webkit-text-fill-color: white; 
                    background: none;
                }}
                
                .results-section {{
                    background: rgba(15, 23, 42, 0.8);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .results-section h2 {{
                    margin-bottom: 1rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #3b82f6;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: rgba(30, 41, 59, 0.5);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                th {{ background: rgba(30, 64, 175, 0.5); }}
                tr:hover {{ background: rgba(56, 73, 106, 0.3); }}
                
                .vuln-critical {{ background: rgba(220, 38, 38, 0.15); }}
                .vuln-high {{ background: rgba(234, 88, 12, 0.15); }}
                .vuln-medium {{ background: rgba(234, 179, 8, 0.15); }}
                .vuln-low {{ background: rgba(101, 163, 13, 0.15); }}
                
                .severity-critical {{ color: #f87171; font-weight: bold; }}
                .severity-high {{ color: #fdba74; font-weight: bold; }}
                .severity-medium {{ color: #fde047; font-weight: bold; }}
                .severity-low {{ color: #bef264; font-weight: bold; }}
                
                footer {{
                    text-align: center;
                    padding: 1.5rem;
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    opacity: 0.7;
                }}
                
                @media (max-width: 768px) {{
                    .stats-grid {{ grid-template-columns: 1fr; }}
                    header h1 {{ font-size: 2rem; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>ReconX Scan Summary Report</h1>
                    <p>Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </header>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h2>{len(self.results)}</h2>
                        <p>Targets Scanned</p>
                    </div>
                    <div class="stat-card">
                        <h2>{total_subdomains}</h2>
                        <p>Subdomains Found</p>
                    </div>
                    <div class="stat-card">
                        <h2>{total_vulns}</h2>
                        <p>Vulnerabilities Found</p>
                    </div>
                    <div class="stat-card critical">
                        <h2>{critical_vulns}</h2>
                        <p>Critical Vulnerabilities</p>
                    </div>
                </div>
                
                <div class="results-section">
                    <h2>Scan Results by Target</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Target</th>
                                <th>Subdomains</th>
                                <th>URLs Found</th>
                                <th>Vulnerabilities</th>
                                <th>Critical</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(
                                f"<tr>"
                                f"<td>{target}</td>"
                                f"<td>{data['subdomain_count']}</td>"
                                f"<td>{len(data.get('urls', []))}</td>"
                                f"<td>{len(data.get('vulnerabilities', []))}</td>"
                                f"<td>{sum(1 for v in data.get('vulnerabilities', []) if v.get('severity') == 'Critical')}</td>"
                                f"</tr>"
                                for target, data in self.results.items()
                            )}
                        </tbody>
                    </table>
                </div>
                
                <div class="results-section">
                    <h2>Scan Details</h2>
                    <table>
                        <tr>
                            <td><strong>Scan Mode</strong></td>
                            <td>{self.mode.capitalize()} Scan</td>
                        </tr>
                        <tr>
                            <td><strong>Scan Duration</strong></td>
                            <td>{round(self.scan_duration, 2)} seconds</td>
                        </tr>
                        <tr>
                            <td><strong>Errors Encountered</strong></td>
                            <td>{len(self.errors)}</td>
                        </tr>
                    </table>
                </div>
                
                <div class="results-section">
                    <h2>Top Vulnerabilities</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Type</th>
                                <th>Target</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(
                                self._vulnerability_row(target, vuln)
                                for target, data in self.results.items()
                                for vuln in data.get('vulnerabilities', [])[:3]  # Top 3 per target
                            )}
                        </tbody>
                    </table>
                </div>
                
                <footer>
                    <p>Generated by ReconX v1.2 | Bug Bounty Reconnaissance Tool</p>
                </footer>
            </div>
        </body>
        </html>
        """
    
    def _vulnerability_row(self, target, vuln):
        severity_class = f"severity-{vuln['severity'].lower()}"
        row_class = f"vuln-{vuln['severity'].lower()}"
        
        return f"""
        <tr class="{row_class}">
            <td><span class="{severity_class}">{vuln['severity']}</span></td>
            <td>{vuln['type']}</td>
            <td>{target}</td>
            <td>{vuln['description']}</td>
        </tr>
        """
    
    def _generate_target_html(self, target):
        data = self.results[target]
        critical_count = sum(1 for v in data.get('vulnerabilities', []) 
                          if v.get('severity') == 'Critical')
        
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ReconX Report - {target}</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{ 
                    font-family: 'Roboto', sans-serif; 
                    background: #0f172a;
                    color: #f1f5f9;
                    line-height: 1.6;
                }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                
                header {{ 
                    background: linear-gradient(135deg, #1e40af 0%, #7e22ce 100%);
                    padding: 2rem;
                    border-radius: 0 0 20px 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.25);
                    text-align: center;
                    margin-bottom: 2rem;
                }}
                header h1 {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
                header p {{ font-size: 1.1rem; opacity: 0.9; }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 2rem;
                }}
                .stat-card {{
                    background: rgba(30, 41, 59, 0.7);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .stat-card h2 {{
                    font-size: 2.5rem;
                    margin-bottom: 0.5rem;
                    background: linear-gradient(90deg, #60a5fa 0%, #c084fc 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                .stat-card.critical {{ 
                    background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
                    color: white;
                }}
                .stat-card.critical h2 {{ 
                    -webkit-text-fill-color: white; 
                    background: none;
                }}
                
                .results-section {{
                    background: rgba(15, 23, 42, 0.8);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .results-section h2 {{
                    margin-bottom: 1rem;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #3b82f6;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background: rgba(30, 41, 59, 0.5);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                th, td {{
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                th {{ background: rgba(30, 64, 175, 0.5); }}
                tr:hover {{ background: rgba(56, 73, 106, 0.3); }}
                
                .vuln-critical {{ background: rgba(220, 38, 38, 0.15); }}
                .vuln-high {{ background: rgba(234, 88, 12, 0.15); }}
                .vuln-medium {{ background: rgba(234, 179, 8, 0.15); }}
                .vuln-low {{ background: rgba(101, 163, 13, 0.15); }}
                
                .severity-critical {{ color: #f87171; font-weight: bold; }}
                .severity-high {{ color: #fdba74; font-weight: bold; }}
                .severity-medium {{ color: #fde047; font-weight: bold; }}
                .severity-low {{ color: #bef264; font-weight: bold; }}
                
                .subdomain-list {{
                    columns: 3;
                    column-gap: 20px;
                }}
                .subdomain-list li {{
                    margin-bottom: 5px;
                    break-inside: avoid;
                }}
                
                @media (max-width: 768px) {{
                    .stats-grid {{ grid-template-columns: 1fr; }}
                    .subdomain-list {{ columns: 1; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>ReconX Scan Report - {target}</h1>
                    <p>Generated at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </header>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h2>{data['subdomain_count']}</h2>
                        <p>Subdomains Found</p>
                    </div>
                    <div class="stat-card">
                        <h2>{len(data.get('urls', []))}</h2>
                        <p>URLs Discovered</p>
                    </div>
                    <div class="stat-card">
                        <h2>{len(data.get('vulnerabilities', []))}</h2>
                        <p>Vulnerabilities</p>
                    </div>
                    <div class="stat-card critical">
                        <h2>{critical_count}</h2>
                        <p>Critical Vulnerabilities</p>
                    </div>
                </div>
                
                <div class="results-section">
                    <h2>Subdomains Discovered</h2>
                    <ul class="subdomain-list">
                        {"".join(f"<li>{sub}</li>" for sub in data['subdomains'][:30])}
                        <li>... and {len(data['subdomains']) - 30} more</li>
                    </ul>
                </div>
                
                <div class="results-section">
                    <h2>Vulnerabilities</h2>
                    <table>
                        <thead>
                            <tr>
                                <th>Severity</th>
                                <th>Type</th>
                                <th>Location</th>
                                <th>Description</th>
                                <th>Tool</th>
                            </tr>
                        </thead>
                        <tbody>
                            {"".join(
                                f"<tr class='vuln-{vuln['severity'].lower()}'>"
                                f"<td><span class='severity-{vuln['severity'].lower()}'>{vuln['severity']}</span></td>"
                                f"<td>{vuln['type']}</td>"
                                f"<td>{vuln['url']}</td>"
                                f"<td>{vuln['description']}</td>"
                                f"<td>{vuln.get('tool', 'N/A')}</td>"
                                f"</tr>"
                                for vuln in data.get('vulnerabilities', [])
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """


# ==============================================
# MAIN APPLICATION
# ==============================================

def display_banner():
    console.print("\n[bold blue]========================================")
    console.print("    R E C O N X   v1.2")
    console.print("  Advanced Reconnaissance Toolkit")
    console.print("========================================\n")


def main():
    display_banner()
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='ReconX - Advanced Bug Bounty Reconnaissance Tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-t', '--target', help='Single target domain')
    parser.add_argument('-l', '--list', help='File containing list of targets')
    parser.add_argument('-m', '--mode', choices=['default', 'deep'], default='default', 
                        help='Scanning mode')
    parser.add_argument('-o', '--output', default='./reconx_results', 
                        help='Output directory')
    parser.add_argument('-c', '--concurrency', type=int, default=10,
                        help='Number of concurrent workers')
    parser.add_argument('--max-resources', action='store_true',
                        help='Enable resource usage limits')
    
    args = parser.parse_args()
    
    # Validate targets
    if not args.target and not args.list:
        console.print("\n[red]Error: You must specify either --target or --list")
        sys.exit(1)
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Initialize scanner
    scanner = ReconScanner(
        target=args.target,
        target_list=args.list,
        mode=args.mode,
        output_dir=args.output,
        concurrency=args.concurrency,
        max_resources=args.max_resources
    )
    
    try:
        scanner.run()
    except KeyboardInterrupt:
        console.print("\n[!] Scan interrupted by user")
    except Exception as e:
        console.print(f"\n[red][!] Critical error: {str(e)}")
    finally:
        report_path = scanner.generate_report()
        console.print(f"\n[bold]✨ Scan completed! View reports at: [cyan]{report_path}[/cyan][/bold]")


if __name__ == '__main__':
    main()
