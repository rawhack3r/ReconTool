"""
phases/report_phase.py
Generate Markdown summary report for target.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from core.utils import read_lines, ensure_dir

def run(
    target,
    outdir: Path,
    tool_cfg: Dict[str, Any],
    ui,
    scan_level="light",
    tool_results=None,
):
    ui.log("Building final report…")

    sub_dir = outdir / "subdomains"
    imp_dir = outdir / "important"
    vuln_dir = outdir / "vuln"
    rep_dir = ensure_dir(outdir / "reports")

    all_subs = read_lines(sub_dir / "all_candidates.txt")
    resolved = read_lines(sub_dir / "resolved.txt")
    alive = read_lines(sub_dir / "alive_httpx.txt")
    emails = read_lines(imp_dir / "emails.txt")
    sens_paths = read_lines(imp_dir / "sensitive_paths.txt")
    owasp_hits = read_lines(vuln_dir / "owasp_top10.txt")
    takeovers = read_lines(vuln_dir / "takeovers.txt")

    md = []
    md.append(f"# NightOwl Report – {target}")
    md.append("")
    md.append(f"**Scan Level:** {scan_level}")
    md.append("")
    md.append("## Stats")
    md.append(f"- Total candidates: {len(all_subs)}")
    md.append(f"- Resolved domains: {len(resolved)}")
    md.append(f"- Alive hosts: {len(alive)}")
    md.append(f"- Emails found: {len(emails)}")
    md.append(f"- Sensitive paths: {len(sens_paths)}")
    md.append(f"- OWASP issues: {len(owasp_hits)}")
    md.append(f"- Takeover signals: {len(takeovers)}")
    md.append("")
    md.append("## Alive Hosts (sample)")
    for line in alive[:50]:
        md.append(f"- {line}")
    if len(alive) > 50:
        md.append(f"... ({len(alive)-50} more)")
    md.append("")
    md.append("## Sensitive Paths (sample)")
    for line in sens_paths[:50]:
        md.append(f"- {line}")
    md.append("")
    md.append("## OWASP Findings")
    for line in owasp_hits:
        md.append(f"- {line}")
    md.append("")
    report_path = rep_dir / "report.md"
    report_path.write_text("\n".join(md))
    ui.log_success(f"Report written: {report_path}")
