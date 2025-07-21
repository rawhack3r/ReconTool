#!/bin/bash

echo "[*] Updating packages and installing dependencies..."
sudo apt update -y
sudo apt install -y git curl python3-pip golang

echo "[*] Installing Go-based tools..."

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/owasp-amass/amass/v4/...@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/lc/gau@latest

echo "[*] Installing Python dependencies..."
pip3 install -r requirements.txt

echo "[*] Setup complete. Please make sure environment PATH includes Go bin folder:"
echo "    export PATH=\$PATH:\$HOME/go/bin"
