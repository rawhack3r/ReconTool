import subprocess
import json
import os
import importlib
from core.error_handler import ErrorHandler
from core.phase_workflow import get_tool_config

class ToolRunner:
    def __init__(self):
        self.output_dir = "outputs/scans"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run(self, tool_name, target, mode, progress_callback=None):
        """Execute a tool and return parsed results"""
        config = get_tool_config(tool_name)
        if not config:
            raise ValueError(f"No configuration found for tool: {tool_name}")
        
        # Handle Python-based tools
        if tool_name.startswith("python_"):
            return self._run_python_tool(tool_name, target, progress_callback)
        
        # Build command
        command = config["command"].format(
            target=target,
            output=os.path.join(self.output_dir, f"{tool_name}_{target}.json")
        )
        
        # Execute command
        try:
            if progress_callback:
                progress_callback(tool_name, 10, "Starting...")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            if progress_callback:
                progress_callback(tool_name, 80, "Processing output...")
            
            # Parse results
            parser_name = config.get("parser", "")
            if parser_name:
                return self._parse_output(parser_name, result.stdout)
            return {"raw": result.stdout}
        
        except subprocess.CalledProcessError as e:
            ErrorHandler.log_error(
                tool_name, 
                f"Command failed: {e.stderr or e.stdout}", 
                target
            )
            raise RuntimeError(f"{tool_name} execution failed") from e
    
    def _run_python_tool(self, tool_name, target, progress_callback):
        """Execute a Python-based tool"""
        module_name = tool_name.replace("python_", "")
        try:
            module = importlib.import_module(f"tools.{module_name}")
            run_func = getattr(module, "run", None)
            if not run_func:
                raise AttributeError(f"No run function in {module_name}")
            
            return run_func(target, progress_callback)
        except Exception as e:
            ErrorHandler.log_error(tool_name, str(e), target)
            raise
    
    def _parse_output(self, parser_name, output):
        """Parse tool output using specified parser"""
        try:
            # Implement parsers for various tools
            if parser_name == "parse_json":
                return json.loads(output)
            elif parser_name == "parse_nuclei":
                return self._parse_nuclei_output(output)
            # Add more parsers as needed
            return {"raw": output}
        except Exception as e:
            ErrorHandler.log_error("ToolRunner", f"Parse error: {str(e)}", "")
            return {"raw": output, "parse_error": str(e)}
    
    def _parse_nuclei_output(self, output):
        """Parse Nuclei vulnerability scanner output"""
        try:
            vulns = []
            for line in output.splitlines():
                if line.strip():
                    vuln = json.loads(line.strip())
                    vulns.append({
                        "template": vuln.get("template-id", ""),
                        "severity": vuln.get("info", {}).get("severity", "unknown"),
                        "url": vuln.get("host", ""),
                        "description": vuln.get("info", {}).get("description", ""),
                        "type": vuln.get("type", "")
                    })
            return {"vulnerabilities": vulns}
        except Exception as e:
            return {"raw": output, "parse_error": str(e)}