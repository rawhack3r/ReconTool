"""
phases/important.py
Collect high-value data: emails, names, sensitive paths, unresolved domains.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any

from core.utils import ensure_dir, read_lines, write_lines
from modules.email_extractor import run_extractor
from modules.profile_finder import run_finder as run_profile
from modules.sensitive_path_finder import run_finder as run_paths

def run(
    target,
    outdir: Path,
    tool_cfg: Dict[str, Any],
    ui,
    scan_level="light",
    tool_results=None,
):
    ui.log("Collecting important data (emails, names, sensitive paths)…")
    imp_dir = ensure_dir(outdir / "important")

    # email extraction from OSINT (gau/wayback) and alive pages (future)
    run_extractor(target, outdir, ui)

    # profile data (names, handles)
    run_profile(target, outdir, ui)

    # juicy endpoints
    run_paths(target, outdir, ui)

    # unresolved from passive
    unresolved_src = outdir / "subdomains" / "unresolved.txt"
    if unresolved_src.exists():
        write_lines(imp_dir / "unresolved.txt", read_lines(unresolved_src))
        ui.log(f"Copied unresolved domain list → important/unresolved.txt")
