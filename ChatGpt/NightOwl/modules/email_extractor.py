import re
from pathlib import Path
from core.utils import write_lines, read_lines

EMAIL_RE = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")

def run_extractor(target, outdir, ui):
    ui.log("Extracting emails (stub)…")
    # later: scan JS, wayback, gau URLs. For now, placeholder.
    emails = set()
    # example: parse gau_urls.txt if exists
    gau = outdir / "osint" / "gau_urls.txt"
    if gau.exists():
        for line in read_lines(gau):
            emails.update(EMAIL_RE.findall(line))
    if emails:
        write_lines(outdir / "important" / "emails.txt", emails)
        ui.log_success(f"Emails found: {len(emails)}")
    else:
        ui.log_warn("No emails found.")
