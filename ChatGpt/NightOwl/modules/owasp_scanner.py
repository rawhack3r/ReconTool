"""
Wrapper that filters Nuclei/other signals into OWASP buckets.
"""
from pathlib import Path
from core.utils import read_lines, write_lines

OWASP_MAP = {
    "xss": "A3-XSS",
    "sqli": "A1-Injection",
    "csrf": "A5-CSRF",
    "ssrf": "A10-SSRF",
    "idor": "A4-IDOR",
}

def run_owasp(target, outdir, ui):
    ui.log("OWASP scan (stub)…")
    npath = outdir / "vuln" / "nuclei_raw.txt"
    if not npath.exists():
        ui.log_warn("No nuclei results available for OWASP mapping.")
        return
    lines = read_lines(npath)
    owasp_hits = []
    for l in lines:
        ll = l.lower()
        for key, label in OWASP_MAP.items():
            if key in ll:
                owasp_hits.append(f"{label}: {l}")
    write_lines(outdir / "vuln" / "owasp_top10.txt", owasp_hits)
    ui.log_success(f"OWASP mapped issues: {len(owasp_hits)}")
