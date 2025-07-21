
import asyncio
import json
import os
from datetime import datetime
from nightowl.core.phase_workflow import PhaseWorkflow
from nightowl.core.error_handler import ErrorHandler
from nightowl.tools.parsers.parse_outputs import ParseOutputs

class NightOwlOrchestrator:
    def __init__(self, target, mode, custom_tools=None):
        self.target = target
        self.mode = mode
        self.custom_tools = custom_tools or []
        self.workflow = PhaseWorkflow(mode, target, custom_tools)
        self.results = {phase: {} for phase in self.workflow.get_phases()}
        self.state_file = f"output/state_{target}.json"

    async def run_workflow(self):
        ErrorHandler.setup_logging()
        state = self.load_state()
        for phase in self.workflow.get_phases():
            if state.get(phase, {}).get("status") == "Completed":
                continue
            self.results[phase]["status"] = "In Progress"
            tools = await self.workflow.get_tools_for_phase(phase)
            tasks = []
            for tool in tools:
                if state.get(phase, {}).get(tool, {}).get("status") != "Completed":
                    tasks.append(self.workflow.run_tool(tool, f"https://{self.target}" if phase in ["Secret Finding", "Endpoint Extraction", "Vulnerability Scanning"] else None))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for tool, result in zip(tools, results):
                self.results[phase][tool] = result
            self.results[phase]["status"] = "Completed"
            self.save_state()

    def load_state(self):
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_state(self):
        os.makedirs("output", exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.results, f, indent=2)

    def retry_failed_tools(self):
        tasks = []
        for phase, data in self.results.items():
            for tool, result in data.items():
                if isinstance(result, dict) and result.get("status") == "Failed":
                    tasks.append(self.workflow.run_tool(tool, f"https://{self.target}" if phase in ["Secret Finding", "Endpoint Extraction", "Vulnerability Scanning"] else None))
        return asyncio.run(asyncio.gather(*tasks, return_exceptions=True))
