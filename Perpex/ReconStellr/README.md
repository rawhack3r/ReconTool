# ReconStellr 🚀

A modular, resume-ready, and beautiful recon automation CLI.

## Highlights

- Multi-tool Subdomain + Asset Enumeration (subfinder, amass, assetfinder, OneForAll)
- Real-time resources + dynamic live dashboard
- Resume on crash/interruption
- Auto-merges results, dedupes, per-target output
- Summary report with success/fail metrics and icons
- Easy to expand via `configs/tools.yaml`

## Usage

1. Install requirements:

pip install -r requirements.txt
bash installer.sh

2. Run your first scan:

python core/main.py --target example.com --mode deep
fo

3. All output saved in `outputs/example.com/`

## FAQ

Q: How do I add new tools?  
A: Edit `configs/tools.yaml`—new tools, output, and integration all plug-and-play.

Q: How to resume scan?  
A: Just rerun the same command; scan will resume from last state.

Q: How to retry failed tools?  
A: At the end, failed tools will be offered for re-run.

## Authors

NightOwl, ReconForge, LLM Stack