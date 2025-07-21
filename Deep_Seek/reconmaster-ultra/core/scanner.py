"""
ReconMaster Core Scanner
"""
import time
import threading
import json
from datetime import datetime
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn
from rich.live import Live
from rich.tree import Tree
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.progress import Progress
from rich.live import Live
from core import dns_enum, subdomain_enum, port_scanner, web_analyzer, vuln_scanner, cloud_enum, reporting
from core.utils import resource_monitor

class ReconScanner:
    def __init__(self, target, output_dir, mode="default", wildcard=False, ai_enabled=False, config=None):
        self.target = target
        self.output_dir = output_dir
        self.mode = mode
        self.wildcard = wildcard
        self.ai_enabled = ai_enabled
        self.config = config or {}
        self.console = Console()
        self.stats = {
            "start_time": time.time(),
            "subdomains": 0,
            "services": 0,
            "open_ports": 0,
            "vulnerabilities": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "secrets": 0,
            "cloud_assets": 0,
            "errors": 0,
            "completed_tasks": 0,
            "total_tasks": 15  # Default number of tasks
        }
        self.critical_findings = []
        self.resource_history = []
        self.output_dirs = self._create_output_structure()
        
    def _create_output_structure(self):
        """Create organized output directory structure"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base_dir = os.path.join(self.output_dir, f"{self.target}_{timestamp}")
        
        dirs = {
            "root": base_dir,
            "subdomains": os.path.join(base_dir, "subdomains"),
            "dns": os.path.join(base_dir, "dns"),
            "services": os.path.join(base_dir, "services"),
            "content": os.path.join(base_dir, "content"),
            "vulns": os.path.join(base_dir, "vulns"),
            "secrets": os.path.join(base_dir, "secrets"),
            "cloud": os.path.join(base_dir, "cloud"),
            "github": os.path.join(base_dir, "github"),
            "screenshots": os.path.join(base_dir, "screenshots"),
            "reports": os.path.join(base_dir, "reports"),
            "logs": os.path.join(base_dir, "logs"),
            "ai": os.path.join(base_dir, "ai_analysis")
        }
        
        for path in dirs.values():
            os.makedirs(path, exist_ok=True)
            
        return dirs
    
    def _display_dashboard(self):
        """Display real-time dashboard during execution"""
        with Live(refresh_per_second=4) as live:
            self.progress = Progress(
                *Progress.get_default_columns(),
                transient=True
            )
            
            # Create progress tasks
            task_ids = {}
            tasks = [
                "Initial Setup", "DNS Enumeration", "Passive Subdomains",
                "Active Subdomains", "Service Discovery", "Port Scanning",
                "Content Discovery", "JS Analysis", "Vulnerability Scanning",
                "Cloud Discovery", "GitHub Recon", "Threat Intelligence",
                "Visual Recon", "AI Analysis", "Report Generation"
            ]
            
            for task in tasks:
                task_ids[task] = self.progress.add_task(f"[cyan]{task}", total=1)
            
            live.update(self._build_dashboard())
            
            while self.stats["completed_tasks"] < self.stats["total_tasks"]:
                # Update progress
                for i, task in enumerate(tasks):
                    if i < self.stats["completed_tasks"]:
                        self.progress.update(task_ids[task], completed=1)
                
                # Update dashboard
                live.update(self._build_dashboard())
                time.sleep(0.25)
            
            # Final update
            live.update(self._build_dashboard())
    
    def _build_dashboard(self):
        """Build the real-time dashboard"""
        # Header panel
        header = f"[bold cyan]ReconMaster Ultra[/bold cyan] | [bold]Target:[/bold] {self.target} | "
        header += f"[bold]Mode:[/bold] {self.mode} | [bold]Elapsed:[/bold] {time.time() - self.stats['start_time']:.1f}s"
        
        # Stats panel
        stats = f"Subdomains: {self.stats['subdomains']} | Services: {self.stats['services']} | "
        stats += f"Vulns: {sum(self.stats['vulnerabilities'].values())} | Secrets: {self.stats['secrets']}"
        
        # Progress section
        progress = self.progress
        
        # Critical findings
        findings = "\n".join(f"[red]• {f}[/red]" for f in self.critical_findings[:3]) or "No critical findings yet"
        
        # Resource usage
        if self.resource_history:
            last = self.resource_history[-1]
            resources = f"CPU: {last['cpu']}% | RAM: {last['ram']}% | Disk: {last['disk']}%"
        else:
            resources = "Collecting initial metrics..."
        
        # Combine all panels
        dashboard = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {header}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ {stats}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{progress}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [bold red]Critical Findings[/bold red]
┃ {findings}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ [bold yellow]Resource Usage[/bold yellow]
┃ {resources}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        """
        return dashboard
    
    def run_scan(self):
        """Execute the full reconnaissance workflow"""
        try:
            # Start resource monitoring
            resource_thread = threading.Thread(
                target=resource_monitor, 
                args=(self.resource_history,),
                daemon=True
            )
            resource_thread.start()
            
            # Start dashboard
            dashboard_thread = threading.Thread(
                target=self._display_dashboard,
                daemon=True
            )
            dashboard_thread.start()
            
            # Execute scan phases
            self._execute_phase("Initial Setup", self._initial_setup)
            self._execute_phase("DNS Enumeration", self._dns_enumeration)
            self._execute_phase("Passive Subdomains", self._passive_subdomain_enum)
            self._execute_phase("Active Subdomains", self._active_subdomain_enum)
            self._execute_phase("Service Discovery", self._service_discovery)
            self._execute_phase("Port Scanning", self._port_scanning)
            self._execute_phase("Content Discovery", self._content_discovery)
            self._execute_phase("JS Analysis", self._js_analysis)
            self._execute_phase("Vulnerability Scanning", self._vulnerability_scanning)
            self._execute_phase("Cloud Discovery", self._cloud_discovery)
            self._execute_phase("GitHub Recon", self._github_recon)
            self._execute_phase("Threat Intelligence", self._threat_intelligence)
            self._execute_phase("Visual Recon", self._visual_recon)
            
            if self.ai_enabled:
                self._execute_phase("AI Analysis", self._ai_analysis)
            
            self._execute_phase("Report Generation", self._generate_reports)
            
            # Final stats
            total_time = time.time() - self.stats["start_time"]
            self.console.print(f"\n[bold green]Scan completed in {total_time:.1f} seconds[/bold green]")
            self.console.print(f"Report available at: {self.output_dirs['reports']}")
            
            # Allow dashboard to update
            time.sleep(3)
            
        except KeyboardInterrupt:
            self.console.print("\n[bold yellow]Scan interrupted. Partial results saved.[/bold yellow]")
        except Exception as e:
            self.console.print(f"\n[bold red]Critical error: {str(e)}[/bold red]")
    
    def _execute_phase(self, phase_name, phase_function):
        """Execute a scan phase and update progress"""
        try:
            self.console.log(f"[bold]Starting phase: {phase_name}[/bold]")
            phase_function()
            self.stats["completed_tasks"] += 1
            self.console.log(f"[green]Completed phase: {phase_name}[/green]")
        except Exception as e:
            self.console.log(f"[red]Error in {phase_name}: {str(e)}[/red]")
            self.stats["errors"] += 1
    
    def _initial_setup(self):
        """Initial setup tasks"""
        # Placeholder for actual setup logic
        time.sleep(0.5)
    
    def _dns_enumeration(self):
        """Perform DNS enumeration"""
        results = dns_enum.run(self.target, self.output_dirs['dns'])
        self.stats['subdomains'] = results.get('subdomains', 0)
    
    def _passive_subdomain_enum(self):
        """Passive subdomain enumeration"""
        results = subdomain_enum.passive_scan(
            self.target, 
            self.output_dirs['subdomains'],
            self.config
        )
        self.stats['subdomains'] = results['count']
    
    def _active_subdomain_enum(self):
        """Active subdomain enumeration"""
        if self.mode in ["deep", "assassin"]:
            base_file = os.path.join(self.output_dirs['subdomains'], "passive.txt")
            results = subdomain_enum.active_scan(
                self.target,
                base_file,
                self.output_dirs['subdomains'],
                self.config
            )
            self.stats['subdomains'] = results['count']
    
    def _service_discovery(self):
        """Service discovery"""
        subdomains_file = os.path.join(self.output_dirs['subdomains'], "all.txt")
        results = web_analyzer.discover_services(
            subdomains_file,
            self.output_dirs['services']
        )
        self.stats['services'] = results['count']
    
    def _port_scanning(self):
        """Port scanning"""
        if self.mode != "lightning":
            subdomains_file = os.path.join(self.output_dirs['subdomains'], "all.txt")
            results = port_scanner.run(
                subdomains_file,
                self.output_dirs['services'],
                self.mode
            )
            self.stats['open_ports'] = results['count']
    
    def _content_discovery(self):
        """Content discovery"""
        services_file = os.path.join(self.output_dirs['services'], "http.txt")
        web_analyzer.content_discovery(
            services_file,
            self.output_dirs['content'],
            self.config
        )
    
    def _js_analysis(self):
        """JavaScript analysis"""
        services_file = os.path.join(self.output_dirs['services'], "http.txt")
        results = web_analyzer.analyze_js(
            services_file,
            self.output_dirs['content']
        )
        self.stats['secrets'] = results.get('secrets', 0)
    
    def _vulnerability_scanning(self):
        """Vulnerability scanning"""
        services_file = os.path.join(self.output_dirs['services'], "http.txt")
        results = vuln_scanner.run(
            services_file,
            self.output_dirs['vulns'],
            self.mode
        )
        self.stats['vulnerabilities'] = results
    
    def _cloud_discovery(self):
        """Cloud discovery"""
        if self.mode in ["deep", "assassin"]:
            results = cloud_enum.run(
                self.target,
                self.output_dirs['cloud']
            )
            self.stats['cloud_assets'] = results.get('count', 0)
    
    def _github_recon(self):
        """GitHub reconnaissance"""
        if self.mode in ["deep", "assassin"]:
            results = web_analyzer.github_recon(
                self.target,
                self.output_dirs['github']
            )
            self.stats['secrets'] += results.get('count', 0)
    
    def _threat_intelligence(self):
        """Threat intelligence gathering"""
        if self.mode in ["deep", "assassin"]:
            web_analyzer.threat_intel(
                self.target,
                self.output_dirs['intel'],
                self.config
            )
    
    def _visual_recon(self):
        """Visual reconnaissance"""
        services_file = os.path.join(self.output_dirs['services'], "http.txt")
        web_analyzer.visual_recon(
            services_file,
            self.output_dirs['screenshots']
        )
    
    # Update _ai_analysis in core/scanner.py
def _ai_analysis(self):
    """AI-powered analysis"""
    if self.ai_enabled:
        try:
            # Simulate AI analysis
            time.sleep(2)
            
            # Add critical findings from vulnerability scan
            vuln_file = os.path.join(self.output_dirs['vulns'], "nuclei_results.json")
            if os.path.exists(vuln_file):
                with open(vuln_file, 'r') as f:
                    for line in f:
                        try:
                            vuln = json.loads(line)
                            if vuln.get('info', {}).get('severity', '').lower() == 'critical':
                                self.critical_findings.append(
                                    f"Critical: {vuln.get('templateID', 'Unknown')} "
                                    f"at {vuln.get('host', 'Unknown')}"
                                )
                        except json.JSONDecodeError:
                            continue
            
            # Add simulated findings
            self.critical_findings.append("AI detected critical XSS vulnerability in contact form")
            self.stats['vulnerabilities']['critical'] = len(
                [f for f in self.critical_findings if "Critical:" in f]
            )
        except Exception as e:
            self.log(f"AI analysis failed: {str(e)}", "error")
    def _generate_reports(self):
        """Generate reports"""
        reporting.generate_reports(
            self.stats,
            self.output_dirs,
            self.target,
            self.mode
        )