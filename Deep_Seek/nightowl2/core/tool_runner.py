import asyncio
import subprocess
import logging
from typing import Callable, Dict, List, Optional

class ToolRunner:
    def __init__(self, config, verbose=False, output_callback=None):
        self.config = config
        self.verbose = verbose
        self.output_callback = output_callback
        self.logger = logging.getLogger("ToolRunner")
        
    async def run_tool(self, tool_func: Callable, phase: str, target: str) -> dict:
        """Run a tool with verbose output handling"""
        try:
            if self.verbose:
                return await self._run_tool_verbose(tool_func, phase, target)
            else:
                return await asyncio.to_thread(tool_func, target)
        except Exception as e:
            self.logger.error(f"Tool {tool_func.__name__} failed: {str(e)}")
            return {"error": str(e)}
            
    async def _run_tool_verbose(self, tool_func: Callable, phase: str, target: str) -> dict:
        """Run a tool with verbose output streaming"""
        tool_name = tool_func.__name__
        
        if self.output_callback:
            self.output_callback(tool_name, f"Starting {tool_name} on {target}")
        
        # Run the tool in a separate process to capture output
        process = await asyncio.create_subprocess_exec(
            *tool_func.get_command(target),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        results = []
        while True:
            line = await process.stdout.readline()
            if not line:
                break
                
            output = line.decode().strip()
            if self.output_callback:
                self.output_callback(tool_name, output)
                
            # Parse results if needed
            if "vulnerability" in output.lower():
                results.append(self._parse_vulnerability(output))
                
        await process.wait()
        
        if self.output_callback:
            self.output_callback(tool_name, f"Tool completed with exit code {process.returncode}")
            
        return {
            "status": "completed" if process.returncode == 0 else "failed",
            "exit_code": process.returncode,
            "results": results
        }
        
    async def run_tool_group(self, group: str, phase: str, target: str) -> Dict[str, dict]:
        """Run a group of tools in parallel"""
        tools = self.config['TOOL_GROUPS'].get(group, [])
        results = {}
        
        # Run tools in parallel
        tasks = []
        for tool_name in tools:
            tool_func = self._get_tool_function(tool_name)
            if tool_func:
                task = asyncio.create_task(self.run_tool(tool_func, phase, target))
                tasks.append((tool_name, task))
        
        # Collect results
        for tool_name, task in tasks:
            results[tool_name] = await task
            
        return results
        
    def _get_tool_function(self, tool_name: str) -> Optional[Callable]:
        """Get tool function by name"""
        # Implementation would map tool names to actual functions
        # For example: "nuclei" -> nuclei_wrapper.run
        return None
        
    def _parse_vulnerability(self, output: str) -> dict:
        """Parse vulnerability from tool output"""
        # Implementation would parse specific tool output
        return {"raw": output}