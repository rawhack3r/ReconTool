#!/bin/bash

# 1. Check Python version
if ! python3 -c "import sys; assert sys.version_info >= (3,9)"; then
    echo "[red]FATAL: Python 3.9+ required"
    exit 1
fi

# 2. Check required binaries
required_tools=("subfinder" "amass" "nuclei" "masscan" "httprobe")
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
    echo "[red]FATAL: Nuclei templates missing"
    exit 1
fi

echo "[green]All dependencies verified!"