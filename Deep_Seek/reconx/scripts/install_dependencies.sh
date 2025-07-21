#!/bin/bash
echo "Installing ReconX dependencies..."
echo "This may take several minutes..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r ../requirements.txt

# Install system dependencies
sudo apt-get update
sudo apt-get install -y jq dnsutils chromium

# Download wordlists
mkdir -p ../config/wordlists
wget https://gist.githubusercontent.com/jhaddix/86a06c5dc309d08580a018c66354a056/raw/96f4e51d96b2203f19f6381c8c545b278eaa0837/all.txt -O ../config/wordlists/subdomains_big.txt
wget https://wordlists-cdn.assetnote.io/data/manual/best-dns-wordlist.txt -O ../config/wordlists/subdomains_top10k.txt

echo "Installation complete! Activate with: source venv/bin/activate"