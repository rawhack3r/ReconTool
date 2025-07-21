FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nmap \
    dnsutils \
    tor \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p /app/outputs/scans \
    /app/outputs/reports \
    /app/outputs/important \
    /app/outputs/vulnerabilities \
    /app/config/wordlists

# Download wordlists
RUN curl -sL https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt -o /app/config/wordlists/subdomains.txt
RUN curl -sL https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-directories.txt -o /app/config/wordlists/directories.txt
RUN curl -sL https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -o /app/config/wordlists/fuzz_params.txt

# Configure Tor
RUN echo "ControlPort 9051" >> /etc/tor/torrc
RUN echo "HashedControlPassword $(tor --hash-password nightowl | tail -n 1)" >> /etc/tor/torrc

# Set entrypoint
ENTRYPOINT ["python", "main.py"]