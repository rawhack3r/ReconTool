# NightOwl CLI Help & Usage

Usage:

  python3 core/main.py --target <domain> [--mode light|deep|custom] [--resume]

Options:

  --target      The domain or subdomain to scan (required)
  --mode        Scan profile: 'light' for fast/basic, 'deep' for comprehensive, 'custom' for manual selection (default: light)
  --resume      Resume previously interrupted scan from last completed phase
  --help        Show this help menu

Examples:

  python3 core/main.py --target example.com --mode light
  python3 core/main.py --target example.com --mode deep
  python3 core/main.py --target example.com --resume

For advanced customization, edit the scan phase definitions and tool configs in:

  ./configs/scan_profiles.yaml
  ./configs/tools.yaml

---

Enjoy your recon workflow with NightOwl!
