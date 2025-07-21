# NightOwl Command Help

## Basic Usage
python3 main.py --target example.com


## Scan Levels
- `light` – fastest, low resource
- `deep` – full recon pipeline
- `custom` – choose tools / phases

## Options
| Flag | Example | Description |
|------|---------|-------------|
| `--target` | `--target example.com` | Single domain |
| `--targets-file` | `--targets-file scope.txt` | One per line |
| `--scan-level` | `--scan-level deep` | light/deep/custom |
| `--tools` | `--tools subfinder,httpx` | Custom tool set |
| `--phases` | `--phases passive,probe,vuln` | Custom phase selection |
| `--resume` | | Resume from last saved state |

See README.md for full docs.
