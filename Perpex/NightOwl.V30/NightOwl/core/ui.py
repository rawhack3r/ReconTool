def draw_banner(target, mode):
    print(f"\n{'='*48}")
    print(f"🦉 NightOwl Recon | Target: {target} | Mode: {mode.upper()}")
    print(f"{'='*48}")

def phase_status(msg):
    print(f"[*] {msg}")

def progress_summary(stats, completed):
    print(f"[+] Tools run: {len(stats)}")
    print(f"[+] Successful: {len(completed['completed'])}")

def print_summary(target, stats, errors):
    print(f"\n{'-'*40}")
    print(f"Summary for: {target}")
    print(f"Tools run: {len(stats)} | Failures: {len(errors)}")
    for err in errors:
        print(f"  ❌ {err.get('tool')}: {err.get('error')}")
    print(f"{'-'*40}")
