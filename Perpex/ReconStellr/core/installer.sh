#!/bin/bash

echo "[+] Installing recon tools..."

sudo apt update
sudo apt install -y golang git python3-pip jq dnsutils

# Ensure Go is setup
export PATH=$PATH:/usr/local/go/bin
export GOROOT=/usr/local/go
export GOPATH=$HOME/go/bin
export PATH=$PATH:$GOPATH

# Install Go tools
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/owasp-amass/amass/v4/...@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/tomnomnom/gau@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

echo "[+] All tools installed! Test them individually before use."
echo "[*] Recommended: Copy binaries from ~/go/bin to /usr/local/bin"
