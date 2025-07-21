#!/bin/bash

# 1. Check Python environment
if ! command -v python3 &> /dev/null; then
    echo "[red]FATAL: Python3 not installed!"
    exit 1
fi

# 2. Check required tools
required_tools=("subfinder" "amass" "nuclei" "masscan" "httprobe" "findomain")
missing=()

for tool in "${required_tools[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        missing+=("$tool")
    fi
done

if [ ${#missing[@]} -gt 0 ]; then
    echo "[red]FATAL: Missing tools: ${missing[*]}"
    exit 1
fi

# 3. Check Nuclei templates
if [ ! -d "~/nuclei-templates/cves" ]; then
    echo "[red]FATAL: Nuclei templates missing!"
    exit 1
fi

echo "[green]✓ All tools installed and configured!"
echo "[cyan]Nuclei templates: $(ls ~/nuclei-templates/cves/ | wc -l) vulnerabilities ready"
