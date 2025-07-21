FROM python:3.10-slim

# Install recon tools
RUN apt-get update && apt-get install -y \
    git \
    golang \
    nmap \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -e . && \
    mkdir -p /app/configs /app/outputs

VOLUME ["/app/configs", "/app/outputs"]
CMD ["reconmaster", "-t", "example.com"]