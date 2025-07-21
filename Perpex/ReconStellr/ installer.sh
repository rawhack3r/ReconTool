#!/bin/bash

echo "[*] Installing recon tools and dependencies..."

sudo apt update
sudo apt install -y golang git python3-pip jq unzip wget

export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/owasp-amass/amass/v4/...@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/lc/gau@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install github.com/tomnomnom/waybackurls@latest

echo "[*] Downloading OneForAll..."
git clone https://github.com/shmilylty/OneForAll.git
cd OneForAll
pip3 install -r requirements.txt
cd ..

echo "[*] Downloading Aquatone..."
wget https://github.com/michenriksen/aquatone/releases/download/v1.7.0/aquatone_linux_amd64_1.7.0.zip
unzip aquatone_linux_amd64_1.7.0.zip
chmod +x aquatone
sudo mv aquatone /usr/local/bin/

echo "[*] Installing gf (for secret finding)..."
go install github.com/tomnomnom/gf@latest
gf -update
echo "[*] All tools installed. Confirm with: subfinder -h, amass -h, etc."
