from core.executor import start_scan
from core.constants import OUTPUT_ROOT
from core.report import generate_markdown_report, render_html_report
from core.phases import load_profile
from core.resume import save_resume_state
from core.ui import draw_banner, print_summary
import argparse


def main():
    parser = argparse.ArgumentParser(description="NightOwl Recon Framework")
    parser.add_argument("--target", required=True, help="Target domain (e.g. example.com)")
    parser.add_argument("--mode", required=True, choices=["light", "deep", "custom"])
    args = parser.parse_args()

    target = args.target.lower()
    mode = args.mode.lower()

    draw_banner(target, mode)

    profile = load_profile(mode)
    target_output_path = OUTPUT_ROOT / target
    target_output_path.mkdir(parents=True, exist_ok=True)

    completed, stats, errors = start_scan(target, profile, target_output_path)

    save_resume_state(completed, target_output_path)
    md_path = generate_markdown_report(target, stats, errors, target_output_path)
    html_path = render_html_report(md_path)

    print_summary(target, stats, errors)
    print(f"\n✅ Markdown Report: {md_path}")
    print(f"🌐 HTML Report    : {html_path}")


if __name__ == "__main__":
    main()
