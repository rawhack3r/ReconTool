from core.tools import ToolRunner
from core.ui import phase_status, progress_summary
from core.extractor import extract_data
from pathlib import Path


def start_scan(target, profile, output_dir, resume_state=None):
    stats = []
    errors = []
    completed = {"completed": []}
    runner = ToolRunner(profile, output_dir)

    for phase in profile["phases"]:
        phase_status(f"→ Starting Phase: {phase.get('name', 'unnamed')}")
        for tool_name in phase.get("tools", []):
            print(f"   🚀 Launching tool: {tool_name}")

            if resume_state and tool_name in resume_state.get("completed", []):
                print(f"   ⏩ Skipping {tool_name} (already completed)")
                continue

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
