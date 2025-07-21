from core.ui import draw_banner, show_checklist
from core.resume_manager import check_resume, save_state
from core.tools_runner import run_tools
from core.report_generator import show_final_summary
from core.error_handler import retry_failed_tools
from core.constants import TOOL_OUTPUT_DIR
from core.progress_tracker import completion_msg
from core.phases import PHASES
from pathlib import Path
import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target domain")
    parser.add_argument("--mode", choices=["light", "deep"], default="light")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    target = args.target
    output_dir = Path(TOOL_OUTPUT_DIR) / target
    output_dir.mkdir(parents=True, exist_ok=True)

    draw_banner(target, args.mode)

    previous_state = check_resume(target)

    results, errors, stats = run_tools(target, args.mode, output_dir, resume_state=previous_state)
    completed_n = sum(1 for v in results.values() if v == "completed")
    completion_str = completion_msg(completed_n, len(results))
    print(f"\n{completion_str}\n")

    show_checklist(results, phase_name="All Phases")

    save_state({"completed": [k for k, v in results.items() if v == "completed"]}, target)

    if any(v=="failed" for v in results.values()):
        retry_failed_tools([k for k, v in results.items() if v=="failed"], target, output_dir)

    show_final_summary(results, errors, output_dir, stats=stats)
