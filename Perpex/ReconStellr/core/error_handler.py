from core.tools_runner import run_tools
from core.ui import update_progress

def retry_failed_tools(failed, target, output_dir):
    print("🔁 Retrying failed tools...\n")
    results, errors = run_tools(target, "resumed", output_dir, retry_only=failed)
    update_progress(results)
    return results, errors
