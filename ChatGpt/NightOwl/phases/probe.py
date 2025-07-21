"""
phases/probe.py
Post-process probing tools (httpx, naabu).
Guarantees alive host list even if tools missing.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from core.utils import read_lines, write_lines, ensure_dir

def run(
    target,
    outdir: Path,
    tool_cfg: Dict[str, Any],
    ui,
    scan_level="light",
    tool_results=None,
):
    ui.log("Processing probe results…")

    sub_dir = outdir / "subdomains"
    probe_dir = ensure_dir(outdir / "probe")

    # Source for alive check
    alive_src = sub_dir / "alive_httpx.txt"   # expected httpx output
    resolved_src = sub_dir / "resolved.txt"
    all_src = sub_dir / "all_candidates.txt"

    if alive_src.exists():
        alive = read_lines(alive_src)
    elif resolved_src.exists():
        # fallback: mark resolved as alive (without protocol)
        alive = [f"http://{h}" for h in read_lines(resolved_src)]
        write_lines(alive_src, alive)
        ui.log_warn("httpx output missing; using resolved hosts as alive fallback.")
    else:
        if all_src.exists():
            alive = [f"http://{h}" for h in read_lines(all_src)]
            write_lines(alive_src, alive)
            ui.log_warn("No resolved hosts; using all candidates as fallback alive list.")
        else:
            alive = []

    write_lines(probe_dir / "alive_hosts.txt", alive)
    ui.log_success(f"Alive hosts (raw/fallback): {len(alive)}")

    # Ports results (if naabu ran)
    naabu_path = probe_dir / "naabu_ports.txt"
    if naabu_path.exists():
        ui.log(f"  [+] naabu ports file present.")
