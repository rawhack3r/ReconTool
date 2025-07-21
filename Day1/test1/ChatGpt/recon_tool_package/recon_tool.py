#!/usr/bin/env python3
"""
recon_tool.py - Unified Bug Bounty Recon Utility

Features:
  - Modular phases: passive, deep_passive, brute, osint, probe, takeover, vuln, optional nmap
  - Configurable commands per phase in COMMANDS dict
  - Error handling: continue on failures, log errors
  - Percentage progress per command
  - Before/After phase banners and step logs
  - Supports default and deep modes
  - Accepts single target, target list, wildcard patterns, wildcard list
  - Easy customization: edit COMMANDS dict

Usage examples:
  ./recon_tool.py --mode default --target example.com
  ./recon_tool.py --mode deep --target-list domains.txt --threads 100
"""
import argparse
import subprocess
import time
import shutil
import os
import sys
from pathlib import Path
import zipfile

COMMANDS = {
    'passive': [
        'subfinder -d {target} -silent -o {out_dir}/subfinder_{target}.txt',
        'amass enum -passive -d {target} -o {out_dir}/amass_{target}.txt'
    ],
    'deep_passive': [
        'python3 oneforall.py --target {target} --outfile {out_dir}/oneforall_{target}.txt'
    ],
    'brute': [
        'dnsgen {out_dir}/passive_subs_{target}.txt -o {out_dir}/permutations_{target}.txt',
        'massdns -r resolvers.txt -t A -o S -w {out_dir}/massdns_{target}.txt {out_dir}/permutations_{target}.txt'
    ],
    'osint': [
        'waybackurls {target} | tee {out_dir}/wayback_{target}.txt',
        'gau {target} | tee -a {out_dir}/wayback_{target}.txt',
        'hakrawler -depth 2 -url {target} -plain > {out_dir}/crawler_{target}.txt'
    ],
    'probe': [
        'cat {out_dir}/passive_subs_{target}.txt | httpx -silent -threads {threads} -o {out_dir}/alive_{target}.txt'
    ],
    'takeover': [
        'subjack -w {out_dir}/alive_{target}.txt -c fingerprints.json -o {out_dir}/takeover_{target}.txt'
    ],
    'vuln': [
        'nuclei -l {out_dir}/alive_{target}.txt -t ~/nuclei-templates/ -o {out_dir}/nuclei_{target}.txt'
    ],
    'nmap': [
        'nmap -iL {out_dir}/alive_{target}.txt -T4 -Pn -p- -oA {out_dir}/nmap_{target}'
    ]
}

ERRORS = []

def run_command(cmd, phase, index, total):
    print(f"\n[~] Phase: {phase} | Command {index}/{total} ({index/total*100:.0f}%)")
    print(f"[>] {cmd}")
    start = time.time()
    try:
        subprocess.run(cmd, shell=True, check=True)
        elapsed = time.time() - start
        print(f"[✔] Completed in {elapsed:.1f}s")
    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start
        print(f"[✘] Failed in {elapsed:.1f}s with return code {e.returncode}")
        ERRORS.append((phase, cmd, f"exit {e.returncode}"))
    except Exception as e:
        elapsed = time.time() - start
        print(f"[✘] Exception in {elapsed:.1f}s: {e}")
        ERRORS.append((phase, cmd, str(e)))

def check_tools():
    required = ['subfinder','amass','httpx','nuclei','subjack','dnsgen',
                'massdns','waybackurls','gau','hakrawler']
    missing = [t for t in required if shutil.which(t) is None]
    if missing:
        print(f"[!] Missing tools: {', '.join(missing)}")
        print("[*] Please ensure all required tools are installed and available in PATH.")
        return False
    return True

def gather_targets(args):
    targets = set()
    if args.target:
        targets.add(args.target)
    if args.target_list:
        for line in Path(args.target_list).read_text().splitlines():
            if line.strip(): targets.add(line.strip())
    if args.wildcard:
        targets.add(args.wildcard)
    if args.wildcard_list:
        for line in Path(args.wildcard_list).read_text().splitlines():
            if line.strip(): targets.add(line.strip())
    return list(targets)

def zip_output_folder(folder_path):
    zipf = zipfile.ZipFile(f"{folder_path}.zip", 'w')
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, folder_path)
            zipf.write(full_path, arcname=arcname)
    zipf.close()
    print(f"[✔] Zipped output to: {folder_path}.zip")

def main():
    parser = argparse.ArgumentParser(description='Unified Recon Tool')
    parser.add_argument('--mode', choices=['default','deep'], default='default')
    parser.add_argument('--target', help='Single domain')
    parser.add_argument('--target-list', help='File with domains')
    parser.add_argument('--wildcard', help='Wildcard domain pattern')
    parser.add_argument('--wildcard-list', help='File with wildcard patterns')
    parser.add_argument('--threads', type=int, default=50)
    parser.add_argument('--out-dir', default='output')
    args = parser.parse_args()

    if not check_tools():
        print("[!] Aborting due to missing tools.")
        return

    targets = gather_targets(args)
    if not targets:
        print("[!] No targets provided.")
        return

    os.makedirs(args.out_dir, exist_ok=True)

    for tgt in targets:
        print(f"\n=== Recon Start: {tgt} (mode: {args.mode}) ===")
        phases = ['passive']
        if args.mode == 'deep':
            phases += ['deep_passive','brute','osint']
        phases += ['probe','takeover','vuln']
        if args.mode == 'deep': phases.append('nmap')

        for phase in phases:
            cmds = COMMANDS.get(phase, [])
            total = len(cmds)
            print(f"\n>>> Starting Phase: {phase} ({total} commands)")
            for idx, template in enumerate(cmds, 1):
                cmd = template.format(target=tgt, threads=args.threads, out_dir=args.out_dir)
                run_command(cmd, phase, idx, total)
            print(f"<<< Completed Phase: {phase}\n")

        if ERRORS:
            print(f"[!] Recon for {tgt} finished with {len(ERRORS)} errors:")
            for ph, cmd, err in ERRORS:
                print(f"  - {ph}: {cmd} -> {err}")
        else:
            print(f"[✔] Recon for {tgt} completed with no errors.")

    zip_output_folder(args.out_dir)

if __name__ == '__main__':
    main()
