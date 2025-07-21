from pathlib import Path
from core.utils import ensure_dir

def run(target, outdir, tool_cfg, ui, scan_level="light"):
    ui.log("Brute phase stub…")
    ensure_dir(outdir / "brute")
    return {"status": "ok"}
