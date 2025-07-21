FROM python:3.10-slim

LABEL maintainer="n00bhack3r"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y curl git gcc golang \
    && go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest \
    && go install github.com/owasp-amass/amass/v4/...@latest \
    && go install github.com/tomnomnom/assetfinder@latest \
    && go install github.com/projectdiscovery/httpx/cmd/httpx@latest \
    && go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH=$PATH:/root/go/bin

ENTRYPOINT ["python3", "core/main.py"]
