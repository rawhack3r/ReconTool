import asyncio
from datetime import datetime
from pathlib import Path
from utils.error_handler import ErrorHandler
from core.state_manager import StateManager
from core.resource_monitor import ResourceMonitor
from core.workflow_engine import WorkflowEngine
from utils.file_manager import FileManager

# Import all scanner classes explicitly
from tools.subdomain.amass import AmassScanner
from tools.subdomain.subfinder import SubfinderScanner
from tools.subdomain.sublist3r import Sublist3rScanner
from tools.subdomain.assetfinder import AssetfinderScanner
from tools.subdomain.findomain import FindomainScanner
from tools.subdomain.crtsh import CrtShScanner
from tools.subdomain.chaos import ChaosScanner
from tools.information.email_extractor import EmailExtractor
from tools.information.name_extractor import NameExtractor
from tools.information.phone_extractor import PhoneExtractor
from tools.information.secret_finder import SecretFinder
from tools.vulnerability.nuclei import NucleiScanner
from tools.vulnerability.naabu import NaabuScanner
from tools.vulnerability.httpx import HttpxScanner
from tools.vulnerability.owasp_scanner import OWASPScanner
from tools.analysis.alive_checker import AliveChecker
from tools.analysis.important_finder import ImportantFinder
from tools.analysis.manual_suggestions import ManualSuggestions
from tools.analysis.endpoint_extractor import EndpointExtractor

class NightOwlOrchestrator:
    def __init__(
        self,
        target: str,
        mode: str = 'deep',
        output_dir: str = "output",
        timeout: int = 300,
        rate_limit: int = 10,
        resume: bool = False,
        custom_tools=None,
        config_file: str = None,
        verbose: bool = False
    ):
        self.target = target
        self.mode = mode
        self.output_dir = Path(output_dir)
        self.timeout = timeout
        self.rate_limit = rate_limit
        self.resume = resume
        self.custom_tools = custom_tools or []
        self.config_file = config_file
        self.verbose = verbose

        self.scan_results = {}
        self.failed_tools = {}
        self.current_phase = 0

        self.state_manager = StateManager(self.output_dir)
        self.resource_monitor = ResourceMonitor()
        self.file_manager = FileManager(self.output_dir)
        self.workflow_engine = WorkflowEngine(self.mode, self.custom_tools)
        self.error_handler = ErrorHandler(self.output_dir)

        self.tools = {}
        self._initialize_tools()

        if self.resume:
            self._restore_previous_state()

        self.scan_start_time = datetime.now()

    def _initialize_tools(self):
        tool_classes = {
            'amass': AmassScanner,
            'subfinder': SubfinderScanner,
            'sublist3r': Sublist3rScanner,
            'assetfinder': AssetfinderScanner,
            'findomain': FindomainScanner,
            'crtsh': CrtShScanner,
            'chaos': ChaosScanner,
            'email_extractor': EmailExtractor,
            'name_extractor': NameExtractor,
            'phone_extractor': PhoneExtractor,
            'secret_finder': SecretFinder,
            'nuclei': NucleiScanner,
            'naabu': NaabuScanner,
            'httpx': HttpxScanner,
            'owasp_scanner': OWASPScanner,
            'alive_checker': AliveChecker,
            'important_finder': ImportantFinder,
            'manual_suggestions': ManualSuggestions,
            'endpoint_extractor': EndpointExtractor
        }
        for name, cls in tool_classes.items():
            try:
                self.tools[name] = cls(timeout=self.timeout, rate_limit=self.rate_limit)
            except Exception as e:
                self.failed_tools[name] = str(e)
                self.error_handler.log_error(name, f"Initialization error: {e}", self.target)

    def _restore_previous_state(self):
        state = self.state_manager.load_state()
        self.scan_results = state.get("scan_results", {})
        self.current_phase = state.get("current_phase", 0)

    async def run(self):
        self.resource_monitor.start()
        phases = self.workflow_engine.get_phases()
        for idx, phase in enumerate(phases, start=1):
            self.current_phase = idx
            if self.resume and idx <= self.current_phase:
                continue
            await self._run_phase(phase)
            self.state_manager.save_state({
                "current_phase": self.current_phase,
                "scan_results": self.scan_results
            })
        self.resource_monitor.stop()
        self._final_summary()

    async def _run_phase(self, phase):
        semaphore = asyncio.Semaphore(20)
        tasks = []

        # Ensure each tool has an entry even if it returns no results
        for tool_name in phase.tools:
            self.scan_results.setdefault(tool_name, [])

        async def run_tool(name):
            try:
                async with semaphore:
                    tool = self.tools.get(name)
                    if not tool:
                        raise RuntimeError("Tool not initialized")
                    results = await tool.scan(self.target)
                    self.scan_results[name] = results
                    await self.file_manager.save_tool_results(name, results)
            except Exception as e:
                self.failed_tools[name] = str(e)
                self.error_handler.log_error(name, str(e), self.target)

        for tool_name in phase.tools:
            tasks.append(asyncio.create_task(run_tool(tool_name)))

        await asyncio.gather(*tasks)

    def _final_summary(self):
        duration = (datetime.now() - self.scan_start_time).total_seconds()
        print(f"Scan complete in {duration:.1f}s; Completed: {len(self.scan_results)}; Failed: {len(self.failed_tools)}")

    def save_state(self):
        self.state_manager.save_state({
            "current_phase": self.current_phase,
            "scan_results": self.scan_results
        })

    def get_scan_statistics(self):
        elapsed = (datetime.now() - self.scan_start_time).total_seconds()
        total_phases = len(self.workflow_engine.get_phases())
        total_tools = len(self.tools)
        completed = len(self.scan_results)
        failed = len(self.failed_tools)
        overall_progress = (completed / total_tools * 100) if total_tools else 0.0
        return {
            "target": self.target,
            "mode": self.mode,
            "overall_progress": overall_progress,
            "resource_usage": self.resource_monitor.get_usage(),
            "current_phase": self.current_phase,
            "total_phases": total_phases,
            "elapsed_time": f"{elapsed:.1f}s",
            "completed_tools": completed,
            "failed_tools": failed
        }

    def get_failed_tools(self):
        return self.failed_tools
