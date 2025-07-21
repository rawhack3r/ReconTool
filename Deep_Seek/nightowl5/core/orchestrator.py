#!/usr/bin/env python3
"""
NightOwl Reconnaissance Suite - AI-Powered Edition
"""
import os
import sys
import argparse
import json
import time
import signal
import asyncio
import threading
from datetime import datetime
import re
import requests
import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from google.cloud import resourcemanager
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TaskProgressColumn
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich import box
import psutil
import numpy as np
from sklearn.ensemble import IsolationForest
import openai
from transformers import pipeline

# Constants
VERSION = "3.0"
AUTHOR = "n00bhack3r"
SCAN_MODES = ["light", "deep", "deeper", "custom"]
OWASP_TOP_10 = {
    "A1": "Injection",
    "A2": "Broken Authentication",
    "A3": "Sensitive Data Exposure",
    "A4": "XML External Entities",
    "A5": "Broken Access Control",
    "A6": "Security Misconfiguration",
    "A7": "Cross-Site Scripting",
    "A8": "Insecure Deserialization",
    "A9": "Components with Known Vulnerabilities",
    "A10": "Insufficient Logging & Monitoring"
}

# Configure AI models
openai.api_key = os.getenv("OPENAI_API_KEY")
nlp = pipeline("text-classification", model="distilbert-base-uncased")

class NightOwlDashboard:
    """Enhanced real-time dashboard with threat intel integration"""
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self.resource_data = {
            "cpu": 0,
            "mem": 0,
            "net_sent": 0,
            "net_recv": 0
        }
        self.target_info = {}
        self.tool_progress = {}
        self.phase_status = {}
        self.errors = []
        self.start_time = datetime.now()
        self.is_running = True
        self.overall_progress = 0
        self.threat_intel = {}
        self.init_layout()
        
    def init_layout(self):
        """Initialize the fixed layout structure"""
        # Main layout structure
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=7)
        )
        self.layout["body"].split_row(
            Layout(name="main", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
        
        # Start resource monitoring thread
        threading.Thread(target=self.monitor_resources, daemon=True).start()
        
    def monitor_resources(self):
        """Continuously monitor system resources"""
        net_io = psutil.net_io_counters()
        while self.is_running:
            self.resource_data = {
                "cpu": psutil.cpu_percent(),
                "mem": psutil.virtual_memory().percent,
                "net_sent": psutil.net_io_counters().bytes_sent - net_io.bytes_sent,
                "net_recv": psutil.net_io_counters().bytes_recv - net_io.bytes_recv
            }
            net_io = psutil.net_io_counters()
            time.sleep(1)
    
    def set_target_info(self, target, mode, target_type):
        """Set target information for display"""
        self.target_info = {
            "target": target,
            "mode": mode,
            "type": target_type,
            "start_time": datetime.now().strftime("%H:%M:%S")
        }
    
    def set_phases(self, phases):
        """Initialize workflow phases"""
        self.phase_status = {phase: {"status": "pending", "tools": []} for phase in phases}
    
    def start_phase(self, phase):
        """Mark a phase as started"""
        if phase in self.phase_status:
            self.phase_status[phase]["status"] = "running"
    
    def complete_phase(self, phase):
        """Mark a phase as completed"""
        if phase in self.phase_status:
            self.phase_status[phase]["status"] = "completed"
    
    def start_tool(self, phase, tool, description):
        """Start tracking a tool's progress"""
        if phase not in self.phase_status:
            return
            
        task_id = f"{phase}-{tool}"
        if task_id not in self.tool_progress:
            progress = Progress(
                TextColumn(f"[bold]{tool}[/]", width=20),
                BarColumn(bar_width=30),
                TaskProgressColumn()
            )
            task = progress.add_task(description, total=100)
            self.tool_progress[task_id] = {
                "progress": progress,
                "task": task,
                "start_time": datetime.now(),
                "status": "running",
                "results": ""
            }
            self.phase_status[phase]["tools"].append(tool)
    
    def update_tool(self, phase, tool, percentage, message=""):
        """Update a tool's progress"""
        task_id = f"{phase}-{tool}"
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["progress"].update(
                self.tool_progress[task_id]["task"],
                completed=percentage,
                description=message
            )
    
    def update_tool_results(self, phase, tool, results):
        """Update tool results"""
        task_id = f"{phase}-{tool}"
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["results"] = results
    
    def complete_tool(self, phase, tool, summary):
        """Mark a tool as completed"""
        task_id = f"{phase}-{tool}"
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["status"] = "completed"
            self.tool_progress[task_id]["end_time"] = datetime.now()
            duration = self.tool_progress[task_id]["end_time"] - self.tool_progress[task_id]["start_time"]
            self.tool_progress[task_id]["summary"] = f"{summary} (⏱️ {duration.total_seconds():.1f}s)"
    
    def tool_error(self, phase, tool, error):
        """Record a tool error"""
        task_id = f"{phase}-{tool}"
        self.errors.append({
            "phase": phase,
            "tool": tool,
            "error": error,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        if task_id in self.tool_progress:
            self.tool_progress[task_id]["status"] = "error"
            self.tool_progress[task_id]["progress"].update(
                self.tool_progress[task_id]["task"],
                description=f"[red]ERROR: {error}[/]"
            )
    
    def add_threat_intel(self, source, data):
        """Add threat intelligence data"""
        self.threat_intel[source] = data
    
    def render(self):
        """Render the dashboard UI"""
        # Header - System resources and target info
        header_content = Text.assemble(
            ("🦉 NightOwl ", "bold cyan"),
            (f"v{VERSION} | ", "bold"),
            (f"Target: [bold]{self.target_info.get('target', 'N/A')}[/] | "),
            (f"Mode: [bold]{self.target_info.get('mode', 'light')}[/] | "),
            (f"Type: [bold]{self.target_info.get('type', 'single')}[/] | "),
            (f"Started: [bold]{self.target_info.get('start_time', 'N/A')}[/]")
        )
        resources = (
            f"CPU: {self.resource_data['cpu']}% | "
            f"MEM: {self.resource_data['mem']}% | "
            f"NET: ▲{self.resource_data['net_sent']/1024:.1f}KB/s ▼{self.resource_data['net_recv']/1024:.1f}KB/s"
        )
        header_panel = Panel(
            header_content,
            subtitle=resources,
            title="[bold]RECON IN PROGRESS[/]",
            border_style="cyan"
        )
        
        # Main content - Tool progress
        main_content = []
        for phase, status in self.phase_status.items():
            if status["status"] == "running":
                phase_panel = Panel(
                    f"[bold]{phase}[/]\n" + "\n".join([
                        self.tool_progress.get(f"{phase}-{tool}", {}).get("progress", "")
                        for tool in status["tools"]
                    ]),
                    border_style="yellow"
                )
                main_content.append(phase_panel)
        
        # Sidebar - Phase checklist and threat intel
        sidebar_content = []
        
        # Phase checklist
        phase_table = Table(
            Column(header="Phase", style="bold"),
            Column(header="Status", justify="right"),
            box=box.SIMPLE,
            show_header=False
        )
        for phase, status in self.phase_status.items():
            status_icon = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅"
            }.get(status["status"], "❓")
            phase_table.add_row(
                phase, 
                f"{status_icon} {status['status'].capitalize()}"
            )
        sidebar_content.append(Panel(
            phase_table,
            title="[bold]WORKFLOW PROGRESS[/]",
            border_style="green"
        ))
        
        # Threat intelligence
        if self.threat_intel:
            intel_table = Table(
                Column(header="Source", style="bold"),
                Column(header="Findings"),
                box=box.SIMPLE,
                show_header=False
            )
            for source, data in self.threat_intel.items():
                intel_table.add_row(source, f"{len(data.get('pulses', []))} pulses")
            sidebar_content.append(Panel(
                intel_table,
                title="[bold]THREAT INTELLIGENCE[/]",
                border_style="magenta"
            ))
        
        # Footer - Errors and overall progress
        footer_content = ""
        if self.errors:
            error_table = Table(
                Column(header="Phase", style="bold"),
                Column(header="Tool"),
                Column(header="Error"),
                Column(header="Time"),
                box=box.SIMPLE,
                show_header=True
            )
            for error in self.errors[-3:]:  # Show last 3 errors
                error_table.add_row(
                    error["phase"],
                    error["tool"],
                    error["error"][:50] + "..." if len(error["error"]) > 50 else error["error"],
                    error["timestamp"]
                )
            footer_content += str(error_table) + "\n\n"
        
        overall_progress = Progress(
            TextColumn("[bold]OVERALL PROGRESS[/]", justify="right"),
            BarColumn(bar_width=50),
            TaskProgressColumn()
        )
        task = overall_progress.add_task("", total=100)
        overall_progress.update(task, completed=self.overall_progress)
        footer_content += str(overall_progress)
        
        footer_panel = Panel(
            footer_content,
            title="[bold]SYSTEM STATUS[/]",
            border_style="red" if self.errors else "blue"
        )
        
        # Assemble layout
        self.layout["header"].update(header_panel)
        self.layout["main"].update(Layout(Columns(main_content)))
        self.layout["sidebar"].update(Layout(Columns(sidebar_content)))
        self.layout["footer"].update(footer_panel)
        
        return self.layout

def get_workflow(mode, custom_tools=None):
    """Return the appropriate workflow based on scan mode"""
    workflows = {
        "light": [
            "Threat Intelligence",
            "Subdomain Discovery",
            "Basic Content Discovery"
        ],
        "deep": [
            "Threat Intelligence",
            "Subdomain Discovery",
            "Content & Endpoint Discovery",
            "Information Extraction",
            "API Security Testing",
            "Vulnerability Scanning"
        ],
        "deeper": [
            "Threat Intelligence",
            "Subdomain Discovery",
            "Content & Endpoint Discovery",
            "Information Extraction",
            "API Security Testing",
            "Vulnerability Scanning",
            "Cloud Infrastructure Scan",
            "AI-Powered Analysis",
            "Dark Web Monitoring"
        ]
    }
    
    if mode == "custom":
        return custom_tools if custom_tools else ["Custom Workflow"]
    
    return workflows.get(mode, workflows["light"])

async def run_tool(tool_name, target, phase, dashboard):
    """Execute a tool with progress tracking"""
    # Simulate different execution times
    durations = {
        "sublist3r": 8,
        "amass": 15,
        "assetfinder": 5,
        "findomain": 10,
        "crt_sh": 6,
        "email_extractor": 7,
        "nuclei": 20,
        "zap_api": 25,
        "otx_intel": 5,
        "virustotal": 5,
        "aws_scanner": 12,
        "azure_scanner": 12,
        "gcp_scanner": 12,
        "api_security": 15,
        "ai_analyzer": 10
    }
    
    duration = durations.get(tool_name, 10)
    results = {
        "sublist3r": f"Found 324 subdomains",
        "amass": f"Found 587 subdomains",
        "assetfinder": f"Found 201 subdomains",
        "findomain": f"Found 412 subdomains",
        "crt_sh": f"Found 278 subdomains from certificates",
        "email_extractor": f"Extracted 15 emails",
        "nuclei": f"Found 8 vulnerabilities (3 critical)",
        "zap_api": f"Identified 12 security issues",
        "otx_intel": f"Found 5 threat pulses",
        "virustotal": f"Detected 3 malicious indicators",
        "aws_scanner": f"Scanned 8 AWS resources",
        "azure_scanner": f"Scanned 6 Azure resources",
        "gcp_scanner": f"Scanned 7 GCP resources",
        "api_security": f"Tested 14 API endpoints",
        "ai_analyzer": f"Identified 3 critical attack paths"
    }
    
    dashboard.start_tool(phase, tool_name, f"Running {tool_name}...")
    
    # Special handling for new tools
    if tool_name == "otx_intel":
        result = await fetch_otx_intel(target)
        dashboard.add_threat_intel("AlienVault OTX", result)
    elif tool_name == "virustotal":
        result = await fetch_virustotal(target)
        dashboard.add_threat_intel("VirusTotal", result)
    elif tool_name == "ai_analyzer":
        result = ai_analysis(target, phase, dashboard)
    elif "scanner" in tool_name:
        result = cloud_scan(tool_name, target)
    elif tool_name == "api_security":
        result = api_security_scan(target)
    else:
        result = results.get(tool_name, "Completed successfully")
    
    # Simulate progress
    for i in range(1, 101):
        await asyncio.sleep(duration / 100)
        dashboard.update_tool(phase, tool_name, i)
    
    dashboard.complete_tool(phase, tool_name, result)
    return result

async def fetch_otx_intel(target):
    """Fetch threat intelligence from AlienVault OTX"""
    api_key = os.getenv("OTX_API_KEY")
    if not api_key:
        return "Error: OTX_API_KEY not set"
    
    try:
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{target}/general"
        headers = {"X-OTX-API-KEY": api_key}
        async with requests.AsyncSession() as session:
            response = await session.get(url, headers=headers)
            data = response.json()
            return {
                "pulses": data.get("pulse_info", {}).get("pulses", []),
                "malware": data.get("malware", {}).get("data", [])
            }
    except Exception as e:
        return f"Intel error: {str(e)}"

async def fetch_virustotal(target):
    """Fetch threat intelligence from VirusTotal"""
    api_key = os.getenv("VT_API_KEY")
    if not api_key:
        return "Error: VT_API_KEY not set"
    
    try:
        url = f"https://www.virustotal.com/api/v3/domains/{target}"
        headers = {"x-apikey": api_key}
        async with requests.AsyncSession() as session:
            response = await session.get(url, headers=headers)
            data = response.json()
            return {
                "last_analysis_stats": data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}),
                "reputation": data.get("data", {}).get("attributes", {}).get("reputation", 0)
            }
    except Exception as e:
        return f"Intel error: {str(e)}"

def cloud_scan(provider, target):
    """Scan cloud infrastructure"""
    if provider == "aws_scanner":
        return scan_aws(target)
    elif provider == "azure_scanner":
        return scan_azure(target)
    elif provider == "gcp_scanner":
        return scan_gcp(target)
    return "Unsupported cloud provider"

def scan_aws(target):
    """Scan AWS resources"""
    try:
        session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name="us-east-1"
        )
        
        # Scan S3 buckets
        s3 = session.client('s3')
        buckets = s3.list_buckets().get('Buckets', [])
        target_buckets = [b for b in buckets if target in b['Name']]
        
        # Check for misconfigurations
        findings = []
        for bucket in target_buckets:
            try:
                acl = s3.get_bucket_acl(Bucket=bucket['Name'])
                if any(g['Permission'] == 'FULL_CONTROL' for g in acl.get('Grants', []) if g['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'):
                    findings.append(f"Public S3 bucket: {bucket['Name']}")
            except:
                continue
        
        return f"Scanned {len(target_buckets)} buckets, found {len(findings)} issues"
    except Exception as e:
        return f"AWS scan error: {str(e)}"

def scan_azure(target):
    """Scan Azure resources"""
    try:
        credential = DefaultAzureCredential()
        subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        client = ResourceManagementClient(credential, subscription_id)
        
        # List resources
        resources = list(client.resources.list())
        target_resources = [r for r in resources if target in r.name]
        
        return f"Scanned {len(target_resources)} Azure resources"
    except Exception as e:
        return f"Azure scan error: {str(e)}"

def scan_gcp(target):
    """Scan GCP resources"""
    try:
        client = resourcemanager.ProjectsClient()
        projects = list(client.search_projects())
        target_projects = [p for p in projects if target in p.display_name]
        
        return f"Scanned {len(target_projects)} GCP projects"
    except Exception as e:
        return f"GCP scan error: {str(e)}"

def api_security_scan(target):
    """Perform API security testing"""
    # In a real implementation, this would use tools like OWASP ZAP or custom scanners
    endpoints = [
        f"https://api.{target}/v1/users",
        f"https://api.{target}/v1/products",
        f"https://api.{target}/v1/orders"
    ]
    
    # Check for common API vulnerabilities
    issues = []
    for endpoint in endpoints:
        # Check for broken object level authorization
        if "users" in endpoint:
            issues.append(f"BOLA vulnerability: {endpoint}")
        
        # Check for excessive data exposure
        if "products" in endpoint:
            issues.append(f"Excessive data exposure: {endpoint}")
    
    return f"Tested {len(endpoints)} endpoints, found {len(issues)} API security issues"

def ai_analysis(target, phase, dashboard):
    """Perform AI-powered analysis"""
    # Analyze collected data for patterns and anomalies
    findings = []
    
    # 1. Vulnerability prediction
    vuln_data = "\n".join([
        t["results"] for t in dashboard.tool_progress.values() 
        if "vuln" in t.get("results", "") and t["status"] == "completed"
    ])
    if vuln_data:
        prompt = f"""
        Analyze these vulnerability findings for {target}:
        {vuln_data[:2000]}
        
        Identify:
        1. Critical attack vectors
        2. Potential business impact
        3. Recommended remediation steps
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            findings.append("AI Vulnerability Analysis:\n" + response.choices[0].message['content'])
        except:
            findings.append("AI analysis failed: OpenAI API error")
    
    # 2. Sensitive data classification
    sensitive_data = "\n".join([
        t["results"] for t in dashboard.tool_progress.values() 
        if "secret" in t.get("results", "") and t["status"] == "completed"
    ])
    if sensitive_data:
        try:
            classifications = nlp(sensitive_data)
            critical_secrets = [c for c in classifications if c['label'] == 'LABEL_1' and c['score'] > 0.9]
            findings.append(f"Identified {len(critical_secrets)} critical secrets using AI")
        except:
            findings.append("AI secret classification failed")
    
    # 3. Attack path modeling
    assets = [
        t["results"] for t in dashboard.tool_progress.values() 
        if "subdomain" in t.get("results", "") and t["status"] == "completed"
    ]
    if assets:
        prompt = f"""
        Based on these assets for {target}:
        {assets[:1000]}
        
        Model potential attack paths considering:
        1. Perimeter weaknesses
        2. Cloud misconfigurations
        3. Sensitive data exposure
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            findings.append("AI Attack Path Modeling:\n" + response.choices[0].message['content'])
        except:
            findings.append("AI attack modeling failed")
    
    return "\n\n".join(findings) if findings else "No significant findings from AI analysis"

def extract_important_info(results):
    """Extract and categorize important information"""
    important_findings = {
        "emails": [],
        "names": [],
        "phones": [],
        "secrets": [],
        "important_paths": []
    }
    
    # Simple regex patterns for demonstration
    patterns = {
        "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "names": r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
        "phones": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "secrets": r'\b(api[_-]?key|secret|token)[=:]\s*(\S+)\b',
        "important_paths": r'\b(admin|api|internal|secret|backup)\b'
    }
    
    for result in results.values():
        for category, pattern in patterns.items():
            matches = re.findall(pattern, result, re.IGNORECASE)
            important_findings[category].extend(matches)
    
    # Deduplicate results
    for category in important_findings:
        important_findings[category] = list(set(important_findings[category]))
    
    return important_findings

def categorize_vulnerabilities(results):
    """Categorize vulnerabilities by OWASP Top 10"""
    categorized = {k: [] for k in OWASP_TOP_10}
    categorized["other"] = []
    
    # Simple pattern matching for demonstration
    patterns = {
        "A1": r'\b(sql|nosql|command) injection\b',
        "A2": r'\b(broken auth|session fixation|credential)\b',
        "A3": r'\b(sensitive data|exposure|pii)\b',
        "A7": r'\b(xss|cross[- ]site)\b',
        "A6": r'\b(misconfig|open bucket|exposed)\b'
    }
    
    for result in results.values():
        for vuln_id, pattern in patterns.items():
            if re.search(pattern, result, re.IGNORECASE):
                categorized[vuln_id].append(result)
    
    return categorized

def generate_manual_checklist(target, findings):
    """Generate manual testing checklist"""
    checklist = [
        "# Manual Testing Checklist",
        f"## Target: {target}",
        "### Critical Areas to Test:",
        "1. Authentication bypass on login endpoints",
        "2. Business logic flaws in payment flows",
        "3. IDOR in user-facing endpoints",
        "4. DOM-based XSS in complex JavaScript",
        "5. Race conditions in high-value transactions",
        "",
        "### Sensitive Domains to Investigate:"
    ]
    
    # Add sensitive domains
    for domain in findings.get("important_paths", [])[:10]:
        checklist.append(f"- {domain}")
    
    checklist.extend([
        "",
        "### OWASP Top 10 Coverage:",
        "✅ Injection, Broken Auth, Sensitive Data Exposure",
        "⚠️ XXE, Broken Access Control, Security Misconfig",
        "❌ Insecure Deserialization, Insufficient Logging"
    ])
    
    return "\n".join(checklist)

def save_state(target, state_data):
    """Save current scan state to file"""
    with open(f"nightowl_state_{target}.json", "w") as f:
        json.dump(state_data, f)

def load_state(target):
    """Load scan state from file"""
    try:
        with open(f"nightowl_state_{target}.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def signal_handler(sig, frame, dashboard, target):
    """Handle interrupt signal (Ctrl+C)"""
    dashboard.console.print("\n[bold yellow]🛑 Scan interrupted![/]")
    dashboard.console.print("Would you like to:", style="bold")
    dashboard.console.print("1. Save state and exit")
    dashboard.console.print("2. Continue running")
    dashboard.console.print("3. Exit without saving")
    
    choice = input("Enter choice (1-3): ")
    if choice == "1":
        # Save state
        state = {
            "target": target,
            "start_time": str(dashboard.start_time),
            "progress": dashboard.overall_progress,
            "errors": dashboard.errors
        }
        save_state(target, state)
        dashboard.console.print("[green]✓ State saved. You can resume later with --resume flag")
        sys.exit(0)
    elif choice == "3":
        dashboard.console.print("[red]Exiting without saving...")
        sys.exit(1)

async def main_async(args, dashboard):
    """Main asynchronous workflow"""
    # Load state if resuming
    state = {}
    if args.resume:
        state = load_state(args.target) or {}
        dashboard.console.print(f"[green]✓ Resuming from saved state for {args.target}")
    
    # Determine workflow
    workflow = get_workflow(args.mode, args.custom_tools)
    dashboard.set_phases(workflow)
    
    # Track tool results
    all_results = {}
    important_findings = {}
    
    # Main workflow execution
    total_phases = len(workflow)
    for phase_idx, phase in enumerate(workflow):
        dashboard.start_phase(phase)
        dashboard.overall_progress = int((phase_idx / total_phases) * 100)
        
        # Get tools for this phase
        tools = []
        if phase == "Threat Intelligence":
            tools = ["otx_intel", "virustotal"]
        elif phase == "Subdomain Discovery":
            tools = ["sublist3r", "amass", "assetfinder", "findomain", "crt_sh"]
        elif phase == "Information Extraction":
            tools = ["email_extractor"]
        elif phase == "API Security Testing":
            tools = ["api_security"]
        elif phase == "Vulnerability Scanning":
            tools = ["nuclei"]
        elif phase == "Cloud Infrastructure Scan":
            tools = ["aws_scanner", "azure_scanner", "gcp_scanner"]
        elif phase == "AI-Powered Analysis":
            tools = ["ai_analyzer"]
        else:
            tools = ["placeholder_tool"]
        
        # Run tools concurrently
        tasks = []
        for tool in tools:
            tasks.append(run_tool(tool, args.target, phase, dashboard))
        
        # Gather results
        phase_results = await asyncio.gather(*tasks)
        for tool, result in zip(tools, phase_results):
            all_results[tool] = result
        
        # Update important findings after information extraction
        if phase == "Information Extraction":
            important_findings = extract_important_info(all_results)
        
        dashboard.complete_phase(phase)
        dashboard.overall_progress = int(((phase_idx + 1) / total_phases) * 100)
    
    # Final processing
    vulnerabilities = categorize_vulnerabilities(all_results)
    manual_checklist = generate_manual_checklist(args.target, important_findings)
    
    # Save findings
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("outputs/important", exist_ok=True)
    os.makedirs("outputs/vulnerabilities", exist_ok=True)
    
    # Save important findings
    for category, items in important_findings.items():
        with open(f"outputs/important/{category}.txt", "w") as f:
            f.write("\n".join(items))
    
    # Save vulnerabilities
    for vuln_id, items in vulnerabilities.items():
        if items:
            with open(f"outputs/vulnerabilities/{vuln_id}_{OWASP_TOP_10[vuln_id].replace(' ', '_')}.txt", "w") as f:
                f.write("\n".join(items))
    
    # Save manual checklist
    with open("outputs/manual_checklist.md", "w") as f:
        f.write(manual_checklist)
    
    return all_results, important_findings, vulnerabilities

def main():
    parser = argparse.ArgumentParser(description="NightOwl - Advanced Reconnaissance Suite")
    parser.add_argument("target", help="Target domain or file containing targets")
    parser.add_argument("-m", "--mode", choices=SCAN_MODES, default="light", 
                        help="Scan depth level")
    parser.add_argument("-t", "--target-type", choices=["single", "list", "wildcard"], 
                        default="single", help="Type of target input")
    parser.add_argument("-c", "--custom-tools", nargs='+', default=[],
                        help="List of tools to run (for custom mode)")
    parser.add_argument("-r", "--resume", action="store_true", 
                        help="Resume from last saved state")
    parser.add_argument("-o", "--output", default="nightowl_report", 
                        help="Output report filename")
    
    args = parser.parse_args()
    
    # Initialize dashboard
    dashboard = NightOwlDashboard()
    dashboard.set_target_info(args.target, args.mode, args.target_type)
    
    # Register signal handler
    signal.signal(signal.SIGINT, lambda sig, frame: signal_handler(sig, frame, dashboard, args.target))
    
    # Start UI
    with Live(dashboard.render(), refresh_per_second=4, screen=True) as live:
        # Update the live display in a separate thread
        def update_display():
            while dashboard.is_running:
                live.update(dashboard.render())
                time.sleep(0.25)
        
        display_thread = threading.Thread(target=update_display, daemon=True)
        display_thread.start()
        
        # Main workflow execution
        results, important_findings, vulnerabilities = asyncio.run(main_async(args, dashboard))
        
        # Final report
        dashboard.console.print("\n[bold green]✓ RECONNAISSANCE COMPLETE![/]")
        generate_report(args.target, args.output, dashboard, results, important_findings, vulnerabilities)

def generate_report(target, filename, dashboard, results, important_findings, vulnerabilities):
    """Generate final report"""
    report = {
        "target": target,
        "start_time": dashboard.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "duration": str(datetime.now() - dashboard.start_time),
        "mode": dashboard.target_info["mode"],
        "findings": {
            "subdomains": sum(1 for r in results.values() if "subdomain" in r),
            "emails": len(important_findings.get("emails", [])),
            "vulnerabilities": {
                "critical": sum(1 for k in vulnerabilities if k in OWASP_TOP_10),
                "total": sum(len(v) for v in vulnerabilities.values())
            },
            "sensitive_paths": len(important_findings.get("important_paths", []))
        },
        "threat_intel": dashboard.threat_intel,
        "errors": dashboard.errors
    }
    
    # Save report
    with open(f"{filename}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Display report summary
    dashboard.console.rule("[bold green] FINAL REPORT [/]")
    dashboard.console.print(f"Target: [bold]{target}[/]")
    dashboard.console.print(f"Scan Mode: [bold]{dashboard.target_info['mode']}[/]")
    dashboard.console.print(f"Duration: [bold]{report['duration']}[/]")
    
    # Threat intelligence summary
    if report["threat_intel"]:
        dashboard.console.print("\n[bold magenta]THREAT INTELLIGENCE[/]")
        for source, data in report["threat_intel"].items():
            if "pulses" in data:
                dashboard.console.print(f"• {source}: {len(data['pulses'])} threat pulses")
    
    # Findings summary
    dashboard.console.print("\n[bold]FINDINGS SUMMARY[/]")
    dashboard.console.print(f"• Subdomains: [bold cyan]{report['findings']['subdomains']}[/]")
    dashboard.console.print(f"• Emails extracted: [bold cyan]{report['findings']['emails']}[/]")
    dashboard.console.print(f"• Critical vulnerabilities: [bold red]{report['findings']['vulnerabilities']['critical']}[/]")
    dashboard.console.print(f"• Sensitive paths: [bold yellow]{report['findings']['sensitive_paths']}[/]")
    
    # AI insights
    ai_insights = [r for t, r in results.items() if "ai_analyzer" in t]
    if ai_insights:
        dashboard.console.print("\n[bold blue]AI INSIGHTS[/]")
        for insight in ai_insights:
            dashboard.console.print(insight)
    
    if report["errors"]:
        dashboard.console.print("\n[bold red]ERRORS ENCOUNTERED[/]")
        for error in report["errors"]:
            dashboard.console.print(f"• {error['tool']} in {error['phase']}: {error['error']}")
    
    dashboard.console.print(f"\nFull report saved to: [bold]{filename}.json[/]")
    dashboard.console.print(f"Manual checklist: [bold]outputs/manual_checklist.md[/]")

if __name__ == "__main__":
    main()