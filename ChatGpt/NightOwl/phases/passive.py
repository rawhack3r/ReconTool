"""
phases/passive.py
Merge passive subdomain tool outputs and perform lightweight DNS resolution.
"""
from __future__ import annotations
import socket
from pathlib import Path
from typing import Dict, Any

from core.utils import ensure_dir, read_lines, write_lines

PASSIVE_OUTPUT_FILES = [
    "subfinder.txt",
    "findomain.txt",
    "assetfinder.txt",
    "amass_passive.txt",
    "crtsh.txt",
]

def _read_tool_file(base_dir: Path, fname: str):
    p = base_dir / "subdomains" / fname
    return read_lines(p, unique=False) if p.exists() else []

def _resolve_host(host: str):
    try:
        data = socket.gethostbyname_ex(host)
        # data: (hostname, aliaslist, ipaddrlist)
        return data[2] if data and len(data) >= 3 else []
    except Exception:
        return []

def run(
    target,
    outdir: Path,
    tool_cfg: Dict[str, Any],
    ui,
    scan_level="light",
    tool_results=None,
):
    ui.log("Merging passive subdomain results…")
    sub_dir = ensure_dir(outdir / "subdomains")

    # Collect raw subdomains
    raw = []
    for fname in PASSIVE_OUTPUT_FILES:
        subs = _read_tool_file(outdir, fname)
        if subs:
            ui.log(f"  [+] {fname}: {len(subs)}")
            raw.extend(subs)

    raw = [s.strip() for s in raw if s.strip()]
    raw = list(dict.fromkeys(raw))  # dedupe preserve order

    all_path = sub_dir / "all_candidates.txt"
    write_lines(all_path, raw)
    ui.log_success(f"Collected {len(raw)} candidate subdomains.")

    # DNS resolve
    ui.log("Resolving candidates (Python socket)…")
    resolved = []
    unresolved = []
    resolved_with_ip = []
    for name in raw:
        ips = _resolve_host(name)
        if ips:
            resolved.append(name)
            resolved_with_ip.append(f"{name},{','.join(ips)}")
        else:
            unresolved.append(name)

    write_lines(sub_dir / "resolved.txt", resolved)
    write_lines(sub_dir / "unresolved.txt", unresolved)
    write_lines(sub_dir / "resolved_with_ip.txt", resolved_with_ip)

    ui.log_success(f"Resolved: {len(resolved)} | Unresolved: {len(unresolved)}")
