"""
phases/vuln.py
Aggregate nuclei + takeover results. Map to OWASP Top 10.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from core.utils import read_lines, write_lines, ensure_dir
from modules.owasp_scanner import run_owasp

def run(
    target,
    outdir: Path,
    tool_cfg: Dict[str, Any],
    ui,
    scan_level="light",
    tool_results=None,
):
    ui.log("Processing vulnerability scan results…")
    vuln_dir = ensure_dir(outdir / "vuln")

    nuclei_raw = vuln_dir / "nuclei_raw.txt"
    if nuclei_raw.exists():
        lines = read_lines(nuclei_raw)
        ui.log(f"  [+] nuclei results: {len(lines)} lines")
    else:
        ui.log_warn("No nuclei results.")
    # OWASP mapping
    run_owasp(target, outdir, ui)

    # Takeover results
    takeover_path = vuln_dir / "takeovers.txt"
    if takeover_path.exists():
        take_lines = read_lines(takeover_path)
        ui.log(f"  [+] takeover findings: {len(take_lines)}")
