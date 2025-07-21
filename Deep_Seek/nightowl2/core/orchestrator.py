import asyncio
import json
import os
import signal
import sys
import traceback
from datetime import datetime
from enum import Enum
import logging

# Core modules
from core.api_security import APISecurityTester
from core.attack_surface import AttackSurfaceMapper
from core.cloud_scanner import CloudScanner
from core.dashboard import NightOwlDashboard
from core.error_handler import ErrorHandler, ErrorLevel, ErrorType
from core.intel_integration import ThreatIntelCollector
from core.parallel_executor import ParallelExecutor, Priority
from core.report_generator import generate_html_report, generate_executive_summary
from core.resilience_manager import ResilienceManager
from core.state_manager import StateManager
from core.tool_runner import ToolRunner
from core.utils import load_config
from tools.vulnerability.nuclei_wrapper import run_nuclei_scan

# Optional modules with fallback
try:
    from tools.blockchain_analyzer import BlockchainAnalyzer
    BLOCKCHAIN_SUPPORT = True
except ImportError:
    BLOCKCHAIN_SUPPORT = False
    logging.warning("Blockchain analysis disabled: dependencies not installed")

try:
    from tools.phishing_detector import PhishingDetector
    PHISHING_DETECTION_SUPPORT = True
except ImportError:
    PHISHING_DETECTION_SUPPORT = False
    logging.warning("Phishing detection disabled: dependencies not installed")

try:
    from core.lightweight_ai import LightweightAI
    AI_ANALYSIS_SUPPORT = True
except ImportError:
    AI_ANALYSIS_SUPPORT = False
    logging.warning("AI analysis disabled: dependencies not installed")

class ScanPhase(Enum):
    THREAT_INTEL = "Threat Intelligence"
    SUBDOMAIN_DISCOVERY = "Subdomain Discovery"
    INFO_EXTRACTION = "Information Extraction"
    API_SECURITY = "API Security Testing"
    VULN_SCANNING = "Vulnerability Scanning"
    CLOUD_SCAN = "Cloud Infrastructure Scan"
    ATTACK_SURFACE = "Attack Surface Mapping"
    AI_ANALYSIS = "AI-Powered Analysis" if AI_ANALYSIS_SUPPORT else "AI Analysis (Disabled)"
    PHISHING_DETECTION = "Phishing Detection" if PHISHING_DETECTION_SUPPORT else "Phishing Detection (Disabled)"
    BLOCKCHAIN_ANALYSIS = "Blockchain Analysis" if BLOCKCHAIN_SUPPORT else "Blockchain Analysis (Disabled)"

class NightOwlOrchestrator:
    def __init__(self, target, mode, target_type, custom_tools, dashboard, resume=False, verbose=False):
        self.target = target
        self.mode = mode
        self.target_type = target_type
        self.custom_tools = custom_tools
        self.dashboard = dashboard
        self.config = load_config()
        self.resume = resume
        self.verbose = verbose
        self.is_running = True
        self.state = self._initialize_state()
        self.error_handler = ErrorHandler()
        self.resilience = ResilienceManager(self.config)
        self.executor = ParallelExecutor(max_workers=self.config.get('MAX_WORKERS', 8))
        self.tool_runner = ToolRunner(self.config, verbose=verbose, output_callback=self._tool_output_callback)
        
        # Initialize core modules
        self.cloud_scanner = CloudScanner(self.config)
        self.api_tester = APISecurityTester(self.config)
        self.threat_intel = ThreatIntelCollector(self.config)
        self.surface_mapper = AttackSurfaceMapper()
        
        # Initialize optional modules
        if PHISHING_DETECTION_SUPPORT:
            self.phishing_detector = PhishingDetector()
        else:
            self.phishing_detector = None
            
        if BLOCKCHAIN_SUPPORT:
            self.blockchain_analyzer = BlockchainAnalyzer()
        else:
            self.blockchain_analyzer = None
            
        if AI_ANALYSIS_SUPPORT:
            self.ai_analyzer = LightweightAI()
        else:
            self.ai_analyzer = None

    def _tool_output_callback(self, tool_name, output_line):
        """Callback to send tool output to dashboard"""
        if self.verbose:
            self.dashboard.show_tool_output(tool_name, output_line)

    def _initialize_state(self):
        if self.resume:
            state = StateManager.load_state(self.target)
            if state:
                return state
        return {
            "target": self.target,
            "mode": self.mode,
            "start_time": datetime.now().isoformat(),
            "progress": 0,
            "completed_phases": [],
            "results": {},
            "errors": []
        }
    
    async def execute_workflow(self):
        self.dashboard.set_target_info(self.target, self.mode, self.target_type)
        phases = self._get_workflow()
        self.dashboard.set_phases([p.value for p in phases])
        
        total_phases = len(phases)
        for phase_idx, phase in enumerate(phases):
            if not self.is_running:
                break
                
            self.dashboard.start_phase(phase_idx)
            self.state['current_phase'] = phase.value
            
            try:
                # Resilience checkpoint
                if self.resilience.should_checkpoint():
                    StateManager.save_state(self.target, self.state)
                
                # Execute phase
                if phase == ScanPhase.THREAT_INTEL:
                    await self._run_threat_intelligence()
                elif phase == ScanPhase.SUBDOMAIN_DISCOVERY:
                    await self._run_subdomain_enumeration()
                elif phase == ScanPhase.INFO_EXTRACTION:
                    await self._run_information_extraction()
                elif phase == ScanPhase.API_SECURITY:
                    await self._run_api_security_testing()
                elif phase == ScanPhase.VULN_SCANNING:
                    await self._run_vulnerability_scanning()
                elif phase == ScanPhase.CLOUD_SCAN:
                    await self._run_cloud_scanning()
                elif phase == ScanPhase.ATTACK_SURFACE:
                    await self._run_attack_surface_mapping()
                elif phase == ScanPhase.AI_ANALYSIS and AI_ANALYSIS_SUPPORT:
                    await self._run_ai_analysis()
                elif phase == ScanPhase.PHISHING_DETECTION and PHISHING_DETECTION_SUPPORT:
                    await self._run_phishing_detection()
                elif phase == ScanPhase.BLOCKCHAIN_ANALYSIS and BLOCKCHAIN_SUPPORT:
                    await self._run_blockchain_analysis()
                
                # Update state
                if self.is_running:
                    self.dashboard.complete_phase(phase_idx)
                    self.state['completed_phases'].append(phase.value)
                    self.state['progress'] = int(((phase_idx + 1) / total_phases) * 100)
                    StateManager.save_state(self.target, self.state)
            except Exception as e:
                error_id = self.error_handler.handle(
                    "Orchestrator",
                    f"Phase {phase.value} failed: {str(e)}",
                    phase.value,
                    ErrorLevel.CRITICAL,
                    ErrorType.UNKNOWN,
                    recoverable=True,
                    retry_count=0
                )
                self.dashboard.show_error(f"Phase failed! Error ID: {error_id['id']}")
                self.state['errors'].append(error_id)
                continue
        
        if self.is_running:
            self._finalize_scan()
    
    async def _run_threat_intelligence(self):
        """Collect threat intelligence from various sources"""
        self.dashboard.start_tool("AlienVault OTX", "Collecting threat intelligence")
        otx_results = await self.threat_intel.fetch_otx_intel(self.target)
        self.state['results']['threat_intel'] = otx_results
        self.dashboard.complete_tool("AlienVault OTX", f"Found {len(otx_results.get('pulses', []))} threat pulses")
        
        self.dashboard.start_tool("VirusTotal", "Checking reputation")
        vt_results = await self.threat_intel.fetch_virustotal(self.target)
        self.state['results']['virustotal'] = vt_results
        stats = vt_results.get('last_analysis_stats', {})
        self.dashboard.complete_tool("VirusTotal", 
            f"Reputation: {vt_results.get('reputation', 0)} | Malicious: {stats.get('malicious', 0)}")
    
    async def _run_subdomain_enumeration(self):
        """Run subdomain enumeration tools in parallel"""
        self.dashboard.start_tool("Subdomain Enumeration", "Running parallel tools")
        tool_group = "subdomain_enum"
        results = await self.tool_runner.run_tool_group(tool_group, ScanPhase.SUBDOMAIN_DISCOVERY.value, self.target)
        self.state['results']['subdomains'] = results
        total_subdomains = sum(len(data) for data in results.values())
        self.dashboard.complete_tool("Subdomain Enumeration", f"Found {total_subdomains} subdomains")
    
    async def _run_information_extraction(self):
        """Extract important information from gathered data"""
        self.dashboard.start_tool("Info Extractor", "Processing data")
        # Consolidate content from all tools
        content = "\n".join([
            str(result) for phase in self.state['results'].values() 
            for tool_result in phase.values()
        ])
        
        # Extract information
        extracted = self.tool_runner.info_extractor.extract_all(content, self.target)
        self.state['results']['information'] = extracted
        
        # Save results
        self.tool_runner.info_extractor.save_results(extracted, self.target)
        
        total_items = sum(len(items) for items in extracted.values())
        self.dashboard.complete_tool("Info Extractor", f"Extracted {total_items} items")
    
    async def _run_api_security_testing(self):
        """Perform API security testing"""
        self.dashboard.start_tool("API Security", "Testing API endpoints")
        try:
            results = await self.api_tester.test_api_security(self.target)
            self.state['results']['api_security'] = results
            self.dashboard.complete_tool("API Security", 
                f"Found {len(results.get('issues', []))} API security issues")
        except Exception as e:
            self.dashboard.tool_error("API Security", str(e))
            self.error_handler.handle(
                "APISecurityTester",
                str(e),
                ScanPhase.API_SECURITY.value,
                ErrorLevel.ERROR,
                ErrorType.API,
                recoverable=True
            )
    
    async def _run_vulnerability_scanning(self):
        """Run vulnerability scanners"""
        self.dashboard.start_tool("Vulnerability Scanning", "Running scanners")
        tool_group = "vulnerability"
        results = await self.tool_runner.run_tool_group(tool_group, ScanPhase.VULN_SCANNING.value, self.target)
        self.state['results']['vulnerabilities'] = results
        total_vulns = sum(len(data) for data in results.values())
        self.dashboard.complete_tool("Vulnerability Scanning", f"Found {total_vulns} vulnerabilities")
    
    async def _run_cloud_scanning(self):
        """Scan cloud infrastructure - Core functionality"""
        providers = self.config['CLOUD_PROVIDERS']
        for provider in providers:
            self.dashboard.start_tool(f"{provider} Scanner", f"Scanning {provider} resources")
            try:
                results = await self.cloud_scanner.scan_provider(provider, self.target)
                self.state['results'].setdefault('cloud', {})[provider] = results
                self.dashboard.complete_tool(f"{provider} Scanner", 
                    f"Found {len(results.get('issues', []))} issues in {len(results.get('resources', []))} resources")
            except Exception as e:
                self.dashboard.tool_error(f"{provider} Scanner", str(e))
                self.error_handler.handle(
                    f"{provider}Scanner",
                    str(e),
                    ScanPhase.CLOUD_SCAN.value,
                    ErrorLevel.ERROR,
                    ErrorType.API,
                    recoverable=True
                )
    
    async def _run_ai_analysis(self):
        """Perform AI-powered analysis - Optional"""
        if not self.ai_analyzer:
            self.dashboard.show_warning("Skipping AI analysis - dependencies not installed")
            return
            
        self.dashboard.start_tool("AI Analyzer", "Performing AI-powered analysis")
        try:
            insights = await self.ai_analyzer.analyze_results(self.target, self.state['results'])
            self.state['results']['ai_insights'] = insights
            self.dashboard.complete_tool("AI Analyzer", 
                f"Generated {len(insights.get('findings', []))} AI insights")
        except Exception as e:
            self.dashboard.tool_error("AI Analyzer", str(e))
            self.error_handler.handle(
                "AIAnalyzer",
                str(e),
                ScanPhase.AI_ANALYSIS.value,
                ErrorLevel.ERROR,
                ErrorType.API,
                recoverable=True
            )
    
    async def _run_attack_surface_mapping(self):
        """Create attack surface visualization"""
        self.dashboard.start_tool("AttackSurfaceMapper", "Building attack surface model")
        try:
            # Add nodes (assets)
            assets = self.state['results'].get('assets', [])
            for asset in assets:
                self.surface_mapper.add_node(
                    asset['id'],
                    asset['type'],
                    asset
                )
            
            # Add connections
            connections = self.state['results'].get('connections', [])
            for conn in connections:
                self.surface_mapper.add_edge(
                    conn['source'],
                    conn['target'],
                    conn['type'],
                    conn.get('weight', 1)
                )
            
            # Generate outputs
            interactive_map = self.surface_mapper.generate_interactive_map(self.target)
            risk_report = self.surface_mapper.generate_risk_report(self.target)
            
            self.state['results']['attack_surface'] = {
                "map_path": interactive_map,
                "report_path": risk_report
            }
            
            self.dashboard.complete_tool("AttackSurfaceMapper", 
                f"Generated attack surface map: {interactive_map}")
        except Exception as e:
            self.dashboard.tool_error("AttackSurfaceMapper", str(e))
            self.error_handler.handle(
                "AttackSurfaceMapper",
                str(e),
                ScanPhase.ATTACK_SURFACE.value,
                ErrorLevel.ERROR,
                ErrorType.UNKNOWN,
                recoverable=True
            )
    
    async def _run_phishing_detection(self):
        """Detect phishing clones of the target - Optional"""
        if not self.phishing_detector:
            self.dashboard.show_warning("Skipping phishing detection - dependencies not installed")
            return
            
        self.dashboard.start_tool("PhishingDetector", "Analyzing subdomains")
        try:
            subdomains = self.state['results']['subdomains']
            # Flatten subdomains from all tools
            all_subs = []
            for tool_result in subdomains.values():
                all_subs.extend(tool_result)
            
            results = self.phishing_detector.detect_clones(self.target, all_subs)
            self.state['results']['phishing_detection'] = results
            self.dashboard.complete_tool("PhishingDetector", 
                f"Found {len(results)} potential phishing sites")
        except Exception as e:
            self.dashboard.tool_error("PhishingDetector", str(e))
            self.error_handler.handle(
                "PhishingDetector",
                str(e),
                ScanPhase.PHISHING_DETECTION.value,
                ErrorLevel.ERROR,
                ErrorType.UNKNOWN,
                recoverable=True
            )
    
    async def _run_blockchain_analysis(self):
        """Analyze blockchain-related assets - Optional"""
        if not self.blockchain_analyzer:
            self.dashboard.show_warning("Skipping blockchain analysis - dependencies not installed")
            return
            
        self.dashboard.start_tool("BlockchainAnalyzer", "Scanning for crypto assets")
        try:
            # Collect all content
            content = "\n".join([
                str(result) for phase in self.state['results'].values() 
                for tool_result in phase.values()
            ])
            results = self.blockchain_analyzer.scan_blockchain_assets(content)
            self.state['results']['blockchain'] = results
            self.dashboard.complete_tool("BlockchainAnalyzer", 
                f"Found {len(results)} crypto addresses")
        except Exception as e:
            self.dashboard.tool_error("BlockchainAnalyzer", str(e))
            self.error_handler.handle(
                "BlockchainAnalyzer",
                str(e),
                ScanPhase.BLOCKCHAIN_ANALYSIS.value,
                ErrorLevel.ERROR,
                ErrorType.UNKNOWN,
                recoverable=True
            )
    
    def _finalize_scan(self):
        """Finalize scan results and generate reports"""
        # Save important findings
        self._save_important_findings()
        
        # Categorize vulnerabilities
        self._categorize_vulnerabilities()
        
        # Generate manual checklist
        self._generate_manual_checklist()
        
        # Generate reports
        report_path = generate_html_report(self.state, self.target)
        summary_path = generate_executive_summary(self.state)
        
        # Generate attack surface if not done
        if 'attack_surface' not in self.state['results']:
            asyncio.run(self._run_attack_surface_mapping())
        
        # Update state
        self.state['end_time'] = datetime.now().isoformat()
        self.state['progress'] = 100
        StateManager.save_state(self.target, self.state)
        
        # Export state for debugging
        StateManager.export_state_json(self.target)
        
        # Generate error report
        error_report = self.error_handler.generate_error_report(self.target)
        self.dashboard.show_info(f"Error report generated: {error_report}")
    
    def handle_interrupt(self, sig, frame):
        """Handle interrupt signal (Ctrl+C)"""
        self.dashboard.show_warning("\n🛑 Scan interrupted!")
        self.dashboard.console.print("Would you like to:", style="bold")
        self.dashboard.console.print("1. Save state and exit")
        self.dashboard.console.print("2. Continue running")
        self.dashboard.console.print("3. Exit without saving")
        
        choice = input("Enter choice (1-3): ")
        if choice == "1":
            StateManager.save_state(self.target, self.state)
            self.dashboard.show_info("✓ State saved. Resume with --resume flag")
            self.is_running = False
            sys.exit(0)
        elif choice == "3":
            self.dashboard.show_error("Exiting without saving...")
            self.is_running = False
            sys.exit(1)
    
    def generate_report(self, filename):
        """Generate final report (legacy)"""
        return generate_html_report(self.state, filename)
    
    def _get_workflow(self):
        """Get workflow based on scan mode"""
        workflows = {
            "light": [
                ScanPhase.SUBDOMAIN_DISCOVERY,
                ScanPhase.INFO_EXTRACTION
            ],
            "deep": [
                ScanPhase.THREAT_INTEL,
                ScanPhase.SUBDOMAIN_DISCOVERY,
                ScanPhase.INFO_EXTRACTION,
                ScanPhase.API_SECURITY,
                ScanPhase.VULN_SCANNING,
                ScanPhase.CLOUD_SCAN,
                ScanPhase.ATTACK_SURFACE
            ],
            "deeper": [
                ScanPhase.THREAT_INTEL,
                ScanPhase.SUBDOMAIN_DISCOVERY,
                ScanPhase.INFO_EXTRACTION,
                ScanPhase.API_SECURITY,
                ScanPhase.VULN_SCANNING,
                ScanPhase.CLOUD_SCAN,
                ScanPhase.ATTACK_SURFACE,
                ScanPhase.PHISHING_DETECTION,
                ScanPhase.BLOCKCHAIN_ANALYSIS,
                ScanPhase.AI_ANALYSIS
            ]
        }
        
        if self.mode == "custom":
            # Map custom tool names to phases
            phase_map = {
                "threat_intel": ScanPhase.THREAT_INTEL,
                "subdomains": ScanPhase.SUBDOMAIN_DISCOVERY,
                "info_extraction": ScanPhase.INFO_EXTRACTION,
                "api_sec": ScanPhase.API_SECURITY,
                "vuln_scan": ScanPhase.VULN_SCANNING,
                "cloud": ScanPhase.CLOUD_SCAN,
                "ai": ScanPhase.AI_ANALYSIS,
                "attack_surface": ScanPhase.ATTACK_SURFACE,
                "phishing": ScanPhase.PHISHING_DETECTION,
                "blockchain": ScanPhase.BLOCKCHAIN_ANALYSIS
            }
            return [phase_map[tool] for tool in self.custom_tools if tool in phase_map]
        return workflows.get(self.mode, workflows["light"])
    
    def _save_important_findings(self):
        """Save important findings to files"""
        # Implementation would extract and save findings
        pass
    
    def _categorize_vulnerabilities(self):
        """Categorize vulnerabilities by OWASP Top 10"""
        # Implementation would categorize vulnerabilities
        pass
    
    def _generate_manual_checklist(self):
        """Generate manual testing checklist"""
        # Implementation would generate checklist
        pass