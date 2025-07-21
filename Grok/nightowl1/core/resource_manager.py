import psutil
import sqlite3
import yaml
import asyncio
from core.error_handler import ErrorHandler
from core.tool_runner import ToolRunner

class AdaptiveExecutor:
    def __init__(self, max_threads=50, max_processes=8):
        self.max_threads = max_threads
        self.max_processes = max_processes
        self.tool_runner = ToolRunner()
        with open("config/tools.yaml", "r") as f:
            self.tools_config = yaml.safe_load(f)

    def adjust_resources(self):
        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        if cpu_usage > 75 or mem_usage > 85:
            self.max_threads = max(1, self.max_threads - 5)
            self.max_processes = max(1, self.max_processes - 2)
        return self.max_threads, self.max_processes

    async def run_tool(self, tool, target):
        try:
            self.adjust_resources()
            tool_config = self.tools_config.get(tool, {})
            command = tool_config.get('command', '').format(target=target, output=f"output/{tool}_{target}.txt")
            result = await self.tool_runner.run_tool_async(command, f"output/{tool}_{target}.txt")
            if result:
                parser = tool_config.get('parser', None)
                if parser:
                    module = __import__(f"tools.{tool.replace('-', '_')}.{tool}_wrapper", fromlist=[parser])
                    parse_func = getattr(module, parser)
                    parsed_result = parse_func(f"output/{tool}_{target}.txt")
                    self.cache_results(tool, target, parsed_result)
                    return parsed_result
            return None
        except Exception as e:
            ErrorHandler.log_error(f"Tool {tool} failed for {target}: {str(e)}")
            return None

    def cache_results(self, tool, target, results):
        try:
            conn = sqlite3.connect('cache.db')
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS results (tool TEXT, target TEXT, results TEXT)")
            c.execute("INSERT INTO results (tool, target, results) VALUES (?, ?, ?)", (tool, target, str(results)))
            conn.commit()
            conn.close()
        except Exception as e:
            ErrorHandler.log_error(f"Caching failed for {tool}: {str(e)}")