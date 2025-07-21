from pathlib import Path
from core.utils import ensure_dir
def run(target, outdir, tool_cfg, ui, scan_level="light"):
    ui.log("Cloud phase stub…")
    ensure_dir(outdir / "cloud")
    return {"status": "ok"}
