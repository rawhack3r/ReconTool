#!/bin/bash
# ReconMaster Ultra Installation Script

echo "Installing ReconMaster Ultra..."

# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip git golang nmap jq

# Install Python dependencies
pip3 install rich psutil requests jinja2 pyyaml

# Install Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install github.com/sensepost/gowitness@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/tomnomnom/waybackurls@latest
go install github.com/lc/gau/v2/cmd/gau@latest
go install github.com/jaeles-project/gospider@latest
go install github.com/hakluke/hakrawler@latest

# Add Go bin to PATH
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
source ~/.bashrc

# Install Amass
sudo snap install amass

# Clone wordlists
mkdir -p resources/wordlists
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt -O resources/wordlists/subdomains.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O resources/wordlists/directories.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-extensions.txt -O resources/wordlists/extensions.txt

echo "Installation complete!"
echo "Please configure your API keys in config/api_keys.yaml"
echo "Run the tool with: python main.py example.com"