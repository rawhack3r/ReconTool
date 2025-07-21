import asyncio
import subprocess
import shutil
import yaml
from pathlib import Path
from typing import Dict, List
from .error_handler import ReconErrorHandler
from .resource_monitor import ResourceMonitor

class ReconOrchestrator:
    def __init__(self):
        self.error_handler = ReconErrorHandler()
        self.scan_phases = ["passive", "active", "intel"]
        self.tools = {phase: [] for phase in self.scan_phases}

    async def load_config(self, config_path: Path) -> bool:
        """Load and validate YAML config"""
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                for phase in self.scan_phases:
                    self.tools[phase] = config.get(phase, [])
            return True
        except Exception as e:
            self.error_handler.log("config", f"Config error: {str(e)}")
            return False

    @ResourceMonitor.track
    async def execute_phase(self, phase: str, target: str) -> (Dict, Dict):
        """Execute all tools in a phase"""
        results = {}
        for tool in self.tools[phase]:
            try:
                # Verify tool exists before execution
                cmd_base = tool["command"].split()[0]
                if not shutil.which(cmd_base):
                    raise FileNotFoundError(f"Command not found: {cmd_base}")
                
                output = await self._run_tool(tool, target)
                if output:
                    results[tool['name']] = output
            except Exception as e:
                self.error_handler.log(tool['name'], str(e))
        return results, {}

    async def _run_tool(self, tool: Dict, target: str) -> List[str]:
        """Execute single tool with timeout"""
        cmd = tool["command"].format(target=target)
        timeout = tool.get("timeout", 300)
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
            if proc.returncode != 0:
                error_msg = stderr.decode().strip()
                raise subprocess.CalledProcessError(
                    proc.returncode, cmd, stdout, stderr
                )
            return stdout.decode().splitlines()
        except asyncio.TimeoutError:
            proc.terminate()
            raise TimeoutError(f"{tool['name']} timed out after {timeout}s")