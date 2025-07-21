import subprocess
import asyncio
from core.error_handler import ErrorHandler

class ToolRunner:
    @staticmethod
    async def run_tool_async(command, output_file):
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return stdout.decode()
            else:
                ErrorHandler.log_error(f"Tool execution failed: {stderr.decode()}")
                return None
        except Exception as e:
            ErrorHandler.log_error(f"Tool execution failed: {str(e)}")
            return None