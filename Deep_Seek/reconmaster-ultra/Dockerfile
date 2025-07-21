FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    nmap \
    jq \
    dnsutils \
    golang \
    && rm -rf /var/lib/apt/lists/*

# Install recon tools
RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest && \
    go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install github.com/sensepost/gowitness@latest && \
    go install github.com/tomnomnom/assetfinder@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/jaeles-project/gospider@latest && \
    go install github.com/hakluke/hakrawler@latest

# Install Amass
RUN go install -v github.com/owasp-amass/amass/v4/...@master

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set Go PATH
ENV PATH=$PATH:/root/go/bin

# Entrypoint
ENTRYPOINT ["python", "main.py"]