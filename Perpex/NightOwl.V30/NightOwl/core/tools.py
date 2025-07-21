import subprocess
from pathlib import Path
from datetime import datetime
from core.config_loader import load_tools_yaml


class ToolRunner:
    def __init__(self, profile, output_dir):
        self.output_dir = output_dir
        self.profile = profile
        self.tools = load_tools_yaml()

    def run(self, tool_name, target):
        tool_def = next((t for t in self.tools if t["name"] == tool_name), None)
        if not tool_def:
            print(f"[⚠️] Tool '{tool_name}' not found in tools.yaml")
            return {"tool": tool_name, "success": False, "error": "Tool not defined."}

        try:
            command = tool_def["command"].format(target=target, output_dir=self.output_dir)
        except KeyError as e:
            err_msg = f"Missing placeholder in command for tool '{tool_name}': {{{str(e)}}}"
            print(f"[❌] {err_msg}")
            return {
                "tool": tool_name,
                "success": False,
                "error": err_msg
            }

        output_path = Path(tool_def.get("output", f"{self.output_dir}/{tool_name}.txt")).expanduser()

        # Important fix: create output parent directory before running the tool
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            start_time = datetime.now()
            print(f"   ⏱️ Running '{tool_name}' for target: {target}")
            result = subprocess.run(command, shell=True, text=True,
                                    capture_output=True, timeout=180)
            duration = (datetime.now() - start_time).total_seconds()

            if result.returncode == 0:
                # Save output to file (some tools output stdout, others write files themselves)
                # Here, we save stdout; adjust if tool writes files directly.
                output_path.write_text(result.stdout or "", encoding="utf-8")
                print(f"   ✅ {tool_name} completed in {duration:.2f}s")
                return {
                    "tool": tool_name,
                    "success": True,
                    "duration": duration,
                    "output": str(output_path)
                }
            else:
                error = result.stderr.strip() or "Unknown error"
                print(f"   ❌ {tool_name} failed with code {result.returncode}: {error}")
                return {
                    "tool": tool_name,
                    "success": False,
                    "duration": duration,
                    "error": error
                }

        except subprocess.TimeoutExpired:
            print(f"   ⌛ {tool_name} timed out.")
            return {
                "tool": tool_name,
                "success": False,
                "duration": 180,
                "error": "Command timed out after 180s"
            }
        except Exception as e:
            print(f"   ❌ Unexpected error in {tool_name}: {e}")
            return {
                "tool": tool_name,
                "success": False,
                "duration": 0,
                "error": f"Internal exception: {e}"
            }
