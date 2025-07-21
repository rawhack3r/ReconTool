import argparse

def parse_args():
    p = argparse.ArgumentParser(description="NightOwl Recon Framework")
    p.add_argument("--target", help="Single domain target (example.com)")
    p.add_argument("--targets-file", help="File containing line-separated targets")
    p.add_argument("--scan-level", choices=["light","deep","custom"], default="light",
                  help="Scan profile to run")
    p.add_argument("--tools", help="Comma-separated tool override (custom mode only)")
    p.add_argument("--phases", help="Comma-separated phase override (custom mode only)")
    p.add_argument("--resume", action="store_true", help="Resume previous scan state")
    return p.parse_args()
