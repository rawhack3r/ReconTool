#!/bin/bash

echo "Installing NightOwl dependencies and tools..."

# Ensure Go is installed
if ! command -v go &>/dev/null; then
    echo "Installing Go..."
    sudo apt update
    sudo apt install -y golang
    export PATH=$PATH:/usr/local/go/bin
    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.zshrc
else
    echo "Go is already installed: $(go version)"
fi

# Ensure Python3 and pip3 are installed
if ! command -v pip3 &>/dev/null; then
    echo "Error: pip3 not found. Installing Python3 and pip3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
else
    echo "Python3 and pip3 are installed: $(python3 --version)"
fi

# Activate virtual environment
VENV_PATH="venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_PATH
fi
source $VENV_PATH/bin/activate

# Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip3 install -r requirements.txt || {
    echo "Error: Failed to install Python dependencies. Check requirements.txt or network connection."
    exit 1
}

# Install external tools
TOOLS=(
    "sublist3r:git clone https://github.com/aboul3la/Sublist3r.git && cd Sublist3r && pip3 install -r requirements.txt && cd .."
    "amass:go install -v github.com/OWASP/Amass/v4/cmd/amass@latest"
    "assetfinder:go install github.com/tomnomnom/assetfinder@latest"
    "findomain:curl -LO https://github.com/Findomain/Findomain/releases/latest/download/findomain-linux && chmod +x findomain-linux && sudo mv findomain-linux /usr/local/bin/findomain"
    "subfinder:go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    "dnsx:go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"
    "gotator:go install github.com/Josue87/gotator@latest"
    "puredns:go install github.com/d3mondev/puredns/v2@latest"
    "trufflehog:go install github.com/trufflesecurity/trufflehog/v3/cmd/trufflehog@latest"
    "gitleaks:go install github.com/gitleaks/gitleaks/v8@latest"
    "katana:go install github.com/projectdiscovery/katana/cmd/katana@latest"
    "ffuf:go install github.com/ffuf/ffuf/v2@latest"
    "waybackurls:go install github.com/tomnomnom/waybackurls@latest"
    "nuclei:go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    "zap:sudo apt update && sudo apt install -y zaproxy"
    "subjack:go install github.com/haccer/subjack@latest"
    "httpx:go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"
)

for tool in "${TOOLS[@]}"; do
    name=$(echo "$tool" | cut -d':' -f1)
    install_cmd=$(echo "$tool" | cut -d':' -f2)
    if command -v "$name" &>/dev/null; then
        echo "$name is already installed."
    else
        echo "Installing $name..."
        if eval "$install_cmd"; then
            echo "$name installed successfully."
        else
            echo "Failed to install $name. Please install manually."
        fi
    fi
done

# Configure API keys
CONFIG_FILE="config/config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    read -p "Enter Amass API key (if any, press Enter to skip): " amass_key
    read -p "Enter Hunter.io API key (if any, press Enter to skip): " hunter_key
    sed -i "s/amass_api_key:.*/amass_api_key: \"$amass_key\"/" "$CONFIG_FILE"
    sed -i "s/hunter_io_api_key:.*/hunter_io_api_key: \"$hunter_key\"/" "$CONFIG_FILE"
else
    echo "Error: $CONFIG_FILE not found."
    exit 1
fi

echo "Installation complete! Run NightOwl with: python3 core/main.py -t <target> -m <mode>"