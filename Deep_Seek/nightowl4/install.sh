
#### install.sh
```bash
#!/bin/bash
echo "[*] Installing NightOwl Reconnaissance Tool"

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies
sudo apt update
sudo apt install -y amass assetfinder subfinder findomain nuclei gospider ffuf waybackurls gau hakrawler naabu masscan wpscan testssl.sh zap mobsfscan

# Download wordlists
mkdir -p config/wordlists
wget https://gist.githubusercontent.com/jhaddix/86a06c5dc309d08580a018c66354a056/raw/96f4e51d96b2203f19f6381c8c545b278eaa0837/all.txt -O config/wordlists/subdomains.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O config/wordlists/directories.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O config/wordlists/parameters.txt
wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-words.txt -O config/wordlists/raft-large.txt

# Create output directories
mkdir -p outputs
mkdir -p state

echo "[+] Installation complete!"
echo "    Run scans: python main.py example.com"
echo "    Start API: python api_server.py"
echo "    Start worker: python worker.py"