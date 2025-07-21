# README.md

# NightOwl Enhanced Reconnaissance Suite

🦉 **NightOwl** is an advanced, AI-powered reconnaissance automation tool designed for comprehensive security testing, bug bounty hunting, and attack surface discovery.

## ✨ Features

### 🔍 **Comprehensive Reconnaissance**
- **Multi-tool Integration**: Seamlessly integrates 15+ reconnaissance tools
- **Intelligent Orchestration**: AI-powered tool selection and workflow optimization
- **Real-time Monitoring**: Live dashboard with progress tracking and resource monitoring
- **Adaptive Execution**: Dynamic resource allocation based on system performance

### 🎯 **Advanced Discovery**
- **Subdomain Enumeration**: Multiple sources including Amass, Subfinder, crt.sh, and more
- **Information Extraction**: Automated email, name, and phone number extraction
- **Secret Detection**: Advanced pattern matching for API keys, passwords, and sensitive data
- **Vulnerability Assessment**: Integrated OWASP Top 10 vulnerability scanning

### 🚀 **Enhanced Capabilities**
- **Three Scan Modes**: Light, Deep, and Custom scanning options
- **State Management**: Resume interrupted scans from last checkpoint
- **Error Recovery**: Automatic retry of failed tools with detailed error reporting
- **Manual Testing Suggestions**: AI-generated recommendations for manual testing

### 📊 **Beautiful Interface**
- **Rich Terminal UI**: Real-time progress with beautiful terminal interface
- **Resource Monitoring**: Live CPU, memory, and network usage tracking
- **Comprehensive Reporting**: HTML, JSON, and CSV export formats
- **Interactive Dashboard**: Phase-based workflow with detailed progress indicators

## 🛠️ Installation

### Prerequisites

Install required tools
sudo apt update && sudo apt install -y python3 python3-pip git nmap

Install Go (for some tools)
wget -q -O - https://git.io/vQhTU | bash

Install subdomain enumeration tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/tomnomnom/assetfinder@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

Install other tools
pip3 install sublist3r


### Quick Setup
Clone repository
git clone https://github.com/yourusername/nightowl-recon.git
cd nightowl-recon

Install dependencies
pip3 install -r requirements.txt

Set up environment
chmod +x setup.sh
./setup.sh

Configure API keys (optional but recommended)
export SHODAN_API_KEY="your-shodan-key"
export VIRUSTOTAL_API_KEY="your-virustotal-key"
export CHAOS_API_KEY="your-chaos-key"



## 🚀 Usage

### Basic Commands
Light scan (basic reconnaissance)
python3 main.py -t example.com -m light

Deep scan (comprehensive reconnaissance)
python3 main.py -t example.com -m deep

Custom scan with specific tools
python3 main.py -t example.com -m custom --tools amass subfinder nuclei

Resume interrupted scan
python3 main.py -t example.com --resume

Run without interactive UI
python3 main.py -t example.com --no-ui



### Advanced Options
Custom output directory
python3 main.py -t example.com -o /path/to/output

Adjust thread count
python3 main.py -t example.com --threads 100

Set custom timeout
python3 main.py -t example.com --timeout 600

Use custom configuration
python3 main.py -t example.com --config custom_config.json



### Scan Modes

#### 🟢 Light Mode
- **Tools**: Subfinder, crt.sh, Email Extractor, Alive Checker
- **Duration**: 5-15 minutes
- **Use Case**: Quick reconnaissance and initial assessment

#### 🔵 Deep Mode
- **Tools**: All available tools (15+ tools)
- **Duration**: 30-120 minutes
- **Use Case**: Comprehensive security assessment

#### 🟡 Custom Mode
- **Tools**: User-selected tools
- **Duration**: Variable
- **Use Case**: Targeted reconnaissance with specific requirements

## 📊 Output Structure

output/
├── scans/
│ ├── subdomains/ # Subdomain enumeration results
│ ├── information/ # Extracted emails, names, phones
│ ├── secrets/ # Discovered secrets and sensitive data
│ ├── vulnerabilities/ # Vulnerability scan results
│ └── analysis/ # Asset analysis and recommendations
├── reports/
│ ├── summary.html # Comprehensive HTML report
│ ├── results.json # Machine-readable JSON report
│ └── findings.csv # CSV export for spreadsheet analysis
├── important/
│ ├── emails.txt # Extracted email addresses
│ ├── names.txt # Extracted names
│ ├── phones.txt # Extracted phone numbers
│ └── sensitive_paths.txt # Important paths and directories
└── logs/
├── scan.log # Detailed scan logs
├── errors.log # Error logs
└── debug.log # Debug information



## 🔧 Configuration

### API Keys Configuration
Set environment variables
export SHODAN_API_KEY="your-shodan-api-key"
export VIRUSTOTAL_API_KEY="your-virustotal-api-key"
export CHAOS_API_KEY="your-chaos-api-key"
export SECURITYTRAILS_API_KEY="your-securitytrails-api-key"



### Custom Configuration File
{
"scan_modes": {
"custom": {
"tools": ["amass", "subfinder", "nuclei"],
"timeout": 300,
"max_threads": 50
}
},
"api_configs": {
"shodan": {
"api_key": "your-api-key",
"rate_limit": 1
}
},
"output_formats": {
"json": true,
"csv": true,
"html": true
}
}

text

## 🎯 Tool Categories

### Subdomain Enumeration
- **Amass**: Advanced subdomain discovery
- **Subfinder**: Fast subdomain enumeration
- **Assetfinder**: Asset discovery
- **Findomain**: Multi-source subdomain finder
- **crt.sh**: Certificate transparency logs
- **Sublist3r**: Python-based subdomain enumeration
- **Chaos**: ProjectDiscovery's subdomain database

### Information Extraction
- **Email Extractor**: Automated email address discovery
- **Name Extractor**: Person name extraction from web pages
- **Phone Extractor**: Phone number discovery
- **Secret Finder**: API keys, passwords, and sensitive data detection

### Vulnerability Assessment
- **Nuclei**: Template-based vulnerability scanner
- **Naabu**: Fast port scanner
- **Httpx**: HTTP toolkit
- **OWASP Scanner**: OWASP Top 10 vulnerability detection

### Asset Analysis
- **Alive Checker**: HTTP/HTTPS service verification
- **Important Finder**: Critical asset identification
- **Manual Suggestions**: AI-powered manual testing recommendations

## 🔍 Manual Testing Checklist

### Authentication Testing
- [ ] Test default credentials
- [ ] Check password policy enforcement
- [ ] Test session management
- [ ] Verify logout functionality
- [ ] Test for session fixation
- [ ] Check for privilege escalation

### Authorization Testing
- [ ] Test horizontal privilege escalation
- [ ] Test vertical privilege escalation
- [ ] Check directory traversal
- [ ] Test insecure direct object references
- [ ] Verify access controls

### Input Validation
- [ ] Test for SQL injection
- [ ] Test for XSS vulnerabilities
- [ ] Check for command injection
- [ ] Test file upload vulnerabilities
- [ ] Check for XXE vulnerabilities

### Session Management
- [ ] Test session timeout
- [ ] Check session token entropy
- [ ] Test for session hijacking
- [ ] Verify secure cookie attributes
- [ ] Test concurrent session handling

## 🚨 Important Security Considerations

### Legal Compliance
- Always obtain proper authorization before testing
- Respect rate limits and terms of service
- Follow responsible disclosure practices
- Comply with local laws and regulations

### Ethical Usage
- Only test systems you own or have explicit permission to test
- Avoid causing disruption to target systems
- Respect privacy and data protection laws
- Use findings responsibly

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
Clone repository
git clone https://github.com/yourusername/nightowl-recon.git
cd nightowl-recon

Install development dependencies
pip3 install -r requirements-dev.txt

Install pre-commit hooks
pre-commit install

Run tests
pytest tests/

text

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) for excellent reconnaissance tools
- [OWASP](https://owasp.org/) for security testing methodologies
- [Rich](https://github.com/Textualize/rich) for beautiful terminal interfaces
- All contributors and the security community

## 📞 Support

- 📧 Email: support@nightowl-recon.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/nightowl-recon/issues)
- 💬 Discord: [Community Server](https://discord.gg/nightowl-recon)
- 📖 Documentation: [Full Documentation](https://nightowl-recon.readthedocs.io/)

---

**Happy Hunting! 🦉**

*Remember: With great power comes great responsibility. Use NightOwl ethically and legally.*