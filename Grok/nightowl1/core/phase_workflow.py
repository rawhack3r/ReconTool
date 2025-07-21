
import shutil
import asyncio
import subprocess
import yaml
import os
from datetime import datetime
from nightowl.core.error_handler import ErrorHandler

class PhaseWorkflow:
    def __init__(self, mode, target, custom_tools=None):
        self.mode = mode
        self.target = target
        self.custom_tools = custom_tools or []
        self.results = {}
        self.errors = []
        with open("config/tools.yaml", "r") as f:
            self.tools_config = yaml.safe_load(f)

    def get_phases(self):
        return [
            "Subdomain Enumeration",
            "Secret Finding",
            "Endpoint Extraction",
            "Vulnerability Scanning",
            "Cloud and IP Discovery"
        ]

    async def get_tools_for_phase(self, phase):
        if phase == "Subdomain Enumeration":
            return await self.get_subdomain_tools()
        elif phase == "Secret Finding":
            return await self.get_secret_finding_tools()
        elif phase == "Endpoint Extraction":
            return await self.get_endpoint_tools()
        elif phase == "Vulnerability Scanning":
            return await self.get_vulnerability_tools()
        elif phase == "Cloud and IP Discovery":
            return await self.get_cloud_tools()
        return []

    async def get_subdomain_tools(self):
        all_tools = {
            "light": ["findomain", "crt_sh", "subfinder"],
            "deep": ["findomain", "crt_sh", "amass", "sublist3r", "subfinder", "assetfinder", "subdomainfinder", "gotator", "puredns", "dnsrecon", "certspotter", "dnsgen"],
            "deeper": ["findomain", "crt_sh", "amass", "sublist3r", "subfinder", "assetfinder", "subdomainfinder", "gotator", "puredns", "dnsrecon", "certspotter", "dnsgen"],
            "custom": self.custom_tools
        }.get(self.mode, [])
        return await self.filter_available_tools(all_tools, "Subdomain Enumeration")

    async def get_secret_finding_tools(self):
        all_tools = ["trufflehog", "gitleaks", "secretfinder", "gf", "emailhunter", "theHarvester"]
        return await self.filter_available_tools(all_tools, "Secret Finding")

    async def get_endpoint_tools(self):
        all_tools = ["katana", "ffuf", "gau", "waybackurls"]
        return await self.filter_available_tools(all_tools, "Endpoint Extraction")

    async def get_vulnerability_tools(self):
        all_tools = ["nuclei", "zap", "metasploit"]
        return await self.filter_available_tools(all_tools, "Vulnerability Scanning")

    async def get_cloud_tools(self):
        all_tools = ["cloud-enum", "dnsdumpster", "shodan"]
        return await self.filter_available_tools(all_tools, "Cloud and IP Discovery")

    async def filter_available_tools(self, tools, phase):
        available_tools = []
        for tool in tools:
            if await self.is_tool_available(tool):
                available_tools.append(tool)
            else:
                self.errors.append(f"Tool {tool} not found, skipping in {phase}")
                ErrorHandler.log_error(f"Tool {tool} not found, skipping in {phase}")
        return available_tools

    async def is_tool_available(self, tool):
        for _ in range(3):
            try:
                if tool in ["crt_sh", "secretfinder", "subdomainfinder", "cloud-enum", "dnsdumpster", "emailhunter"]:
                    return True
                process = await asyncio.create_subprocess_exec(
                    'which', tool, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await process.communicate()
                if stdout.strip():
                    return True
                await asyncio.sleep(1)
            except Exception as e:
                ErrorHandler.log_error(f"Error checking tool {tool} availability: {e}")
                await asyncio.sleep(1)
        return False

    async def run_tool(self, tool, url=None):
        start_time = datetime.now()
        output_file = f"output/{tool}_{self.target}.txt"
        command = self.tools_config[tool]["command"].format(target=self.target, url=url or f"https://{self.target}", output=output_file)
        result_count = 0
        for attempt in range(3):
            try:
                with open(f"logs/tool_output_{tool}.log", "a") as log_file:
                    log_file.write(f"\n[{start_time}] Running {tool}...\n")
                    process = await asyncio.create_subprocess_shell(
                        command, stdout=log_file, stderr=log_file
                    )
                    await process.communicate()
                    if process.returncode == 0:
                        try:
                            with open(output_file, "r") as f:
                                result_count = len([line for line in f if line.strip()])
                        except:
                            pass
                        ErrorHandler.log_info(f"Tool {tool} completed: {result_count} results")
                        return {
                            "status": "Completed",
                            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "duration": str(datetime.now() - start_time),
                            "results": result_count
                        }
                    ErrorHandler.log_error(f"Tool {tool} failed on attempt {attempt + 1}")
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                ErrorHandler.log_error(f"Tool {tool} execution error: {e}")
                await asyncio.sleep(2 ** attempt)
        self.errors.append(f"Tool {tool} failed after 3 attempts")
        return {
            "status": "Failed",
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": str(datetime.now() - start_time),
            "results": 0
        }