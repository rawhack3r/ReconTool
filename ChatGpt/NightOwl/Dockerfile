FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    NIGHTOWL_HOME=/opt/nightowl

WORKDIR ${NIGHTOWL_HOME}

# System deps (add more: dig, whois, curl, git, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl jq dnsutils whois git wget build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . ${NIGHTOWL_HOME}

# Default: show help
ENTRYPOINT ["python3", "main.py", "--help"]
