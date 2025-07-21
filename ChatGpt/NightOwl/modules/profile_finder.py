# stub – later: scrape homepage & contact pages
from pathlib import Path
from core.utils import write_lines

def run_finder(target, outdir, ui):
    ui.log("Profile finder (stub)…")
    write_lines(outdir / "important" / "names.txt", [])
