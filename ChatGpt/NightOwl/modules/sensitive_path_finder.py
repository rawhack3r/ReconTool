# scan collected URLs for juicy keywords
from core.utils import read_lines, write_lines

KEYWORDS = ["admin","login","config","backup",".git",".env","staging","auth","portal"]

def run_finder(target, outdir, ui):
    ui.log("Sensitive path finder (stub)…")
    urls_file = outdir / "osint" / "gau_urls.txt"
    paths = []
    if urls_file.exists():
        for line in read_lines(urls_file):
            if any(k in line.lower() for k in KEYWORDS):
                paths.append(line)
    write_lines(outdir / "important" / "sensitive_paths.txt", paths)
    ui.log_success(f"Sensitive paths: {len(paths)}")
