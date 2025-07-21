# Base image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    nmap \
    dnsutils \
    tor \
    golang-go \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
ENV PATH=$PATH:/root/go/bin

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install Playwright browsers
RUN playwright install chromium

# Set entrypoint
ENTRYPOINT ["python3", "main.py"]