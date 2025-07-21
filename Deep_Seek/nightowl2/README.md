# 🦉 NightOwl Reconnaissance Suite

Advanced reconnaissance tool with AI-powered analysis, cloud scanning, and threat intelligence.

![NightOwl Dashboard](assets/dashboard-screenshot.png)

## Features
- **AI-Powered Analysis**: Vulnerability assessment and attack path modeling
- **Cloud Security**: AWS, Azure, and GCP resource scanning
- **API Security**: Automated API endpoint testing
- **Threat Intelligence**: AlienVault OTX and VirusTotal integration
- **Real-time Dashboard**: Beautiful terminal interface with progress tracking
- **Attack Surface Visualization**: Interactive network graph of discovered assets
- **Blockchain Analysis**: Crypto wallet detection and risk assessment

## Installation
```bash
git clone https://github.com/n00bhack3r/nightowl.git
cd nightowl
pip install -r requirements.txt

# Set API keys (recommended: add to .env file)
export OPENAI_API_KEY="your_openai_key"
export OTX_API_KEY="your_alienvault_key"
export VT_API_KEY="your_virustotal_key"
export AWS_ACCESS_KEY_ID="your_aws_key"
export AWS_SECRET_ACCESS_KEY="your_aws_secret"
export AZURE_SUBSCRIPTION_ID="your_azure_sub_id"

Usage

# Light scan
./main.py example.com -m light

# Deep scan (recommended)
./main.py example.com -m deep

# Full scan with AI and cloud
./main.py example.com -m deeper

# Custom scan
./main.py example.com -m custom -c amass nuclei

# Resume interrupted scan
./main.py example.com -m deep -r

Workflow Modes



Mode	                 Description	                                Tools Included

light	            Basic reconnaissance	                 Subdomain discovery, Information extraction

deep	        Comprehensive security assessment	    + Threat intel, Vuln scanning, API security

deeper	        Complete attack surface analysis	    + Cloud scanning, AI analysis, Attack mapping




Output Structure


outputs/
├── important/            # Critical findings (emails, secrets)
├── vulnerabilities/      # Categorized vulnerabilities
├── cloud/                # Cloud scan results
├── api_security/         # API security findings
├── threat_intel/         # Threat intelligence reports
├── ai_insights/          # AI-generated analysis
├── attack_surface/       # Attack map visualizations
├── blockchain/           # Blockchain analysis results
└── reports/              # HTML and text reports


AI-Powered Capabilities
Vulnerability Analysis: Prioritize critical security issues

Secret Detection: Identify exposed credentials using NLP

Attack Path Modeling: Visualize potential attack vectors

Phishing Detection: Find clone sites using similarity analysis

Zero-Day Detection: Identify novel attack patterns

Contribution
We welcome contributions! Please submit PRs with:

New tool integrations

Additional cloud providers

Enhanced AI models

UI improvements

License

NightOwl is released under the MIT License. See LICENSE for details.


### Final Tools Implementations:

**1. tools/email_extractor.py**
```python
import re

def extract_emails(text):
    """Extract email addresses from text"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return list(set(re.findall(pattern, text)))

