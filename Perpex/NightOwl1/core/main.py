import argparse
from pathlib import Path
import logging
from core.banner import draw_banner
from core.resume_manager import check_resume, save_state
from core.tools_runner import run_tools
from core.report_generator import show_final_summary
from core.error_handler import retry_failed_tools
from core.constants import TOOL_OUTPUT_DIR
from core.ui import show_checklist
from core.progress_tracker import completion_msg


logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("nightowl.log"),
        logging.StreamHandler()
    ]
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--mode", choices=["light", "deep"], default="light")
    args = parser.parse_args()

    target = args.target
    mode = args.mode
    output_dir = Path(TOOL_OUTPUT_DIR) / target
    output_dir.mkdir(parents=True, exist_ok=True)

    draw_banner(target, mode)

    previous_state = check_resume(target)

    results, errors, stats = run_tools(target, mode, output_dir, resume_state=previous_state)

    completed_n = sum(1 for v in results.values() if v == "completed")
    print(f"\n{completion_msg(completed_n, len(results))}\n")

    show_checklist(results, "All Phases")

    save_state({"completed": [k for k, v in results.items() if v == "completed"]}, target)

    if any(v == "failed" for v in results.values()):
        retry_failed_tools([k for k, v in results.items() if v == "failed"], target, output_dir)

    show_final_summary(results, errors, output_dir, stats)


if __name__ == "__main__":
    main()
