from core.tools import ToolRunner
from core.ui import phase_status, progress_summary
from core.extractor import extract_data
from pathlib import Path  # ✅ Needed to use `Path()`

def start_scan(target, profile, output_dir, resume_state=None):
    stats = []        # Stores each tool’s result
    errors = []       # Stores failed tools
    completed = {"completed": []}  # Resume-friendly result

    runner = ToolRunner(profile, output_dir)

    for phase in profile["phases"]:
        phase_status("→ Starting Phase")

        for tool_name in phase["tools"]:
            # ✅ Avoid re-running already completed tools (if resume enabled)
            if resume_state and tool_name in resume_state.get("completed", []):
                continue

            # ✅ Run the tool now
            result = runner.run(tool_name, target)
            stats.append(result)

            if result["success"]:
                completed["completed"].append(tool_name)
                output_file = Path(result["output"])
                if output_file.exists():
                    extract_data(output_file, output_dir)
            else:
                errors.append({
                    "tool": tool_name,
                    "error": result.get("error", "Unknown Error")
                })

        progress_summary(stats, completed)

    return completed, stats, errors
