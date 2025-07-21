import openai
import json
from core.error_handler import ErrorHandler

class AIOrchestrator:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.tools = {
            "subfinder": "Passive subdomain enumeration",
            "assetfinder": "Passive subdomain enumeration",
            "findomain": "Fast subdomain discovery",
            "amass": "Comprehensive subdomain enumeration",
            "sublist3r": "OSINT-based subdomain enumeration",
            "gotator": "Permutation-based subdomain enumeration",
            "puredns": "Active subdomain resolution",
            "subdomainfinder": "Passive subdomain enumeration",
            "trufflehog": "Secret detection in web content",
            "gitleaks": "Secret detection in repositories",
            "secretfinder": "Secret detection in JavaScript",
            "katana": "Web crawling for endpoints",
            "ffuf": "Directory fuzzing",
            "gau": "URL extraction from OTX",
            "waybackurls": "Historical URL extraction",
            "nuclei": "Vulnerability scanning",
            "zap": "Web vulnerability scanning",
            "metasploit": "Advanced vulnerability checks",
            "cloudenum": "Cloud resource enumeration",
            "azureenum": "Azure resource enumeration",
            "gcpenum": "GCP resource enumeration"
        }

    def recommend_tools(self, target, history, mode, target_type):
        prompt = f"""
        Target: {target}
        Scan Mode: {mode}
        Target Type: {target_type}
        Previous findings: {json.dumps(history)[:1000]}
        Available tools: {list(self.tools.keys())}
        Recommend 3-5 tools with parameters for {mode} mode, prioritizing subdomain enumeration, secret finding, and sensitive domain detection (e.g., admin, api).
        Output format: 
        - tool_name: reason, parameters
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            return self.parse_recommendations(response.choices[0].message['content'])
        except Exception as e:
            ErrorHandler.log_error(f"AI recommendation failed: {str(e)}")
            return []

    def parse_recommendations(self, response):
        recommendations = []
        lines = response.strip().split("\n")
        for line in lines:
            if line.startswith("-"):
                tool, reason_params = line[1:].split(":", 1)
                tool = tool.strip()
                reason, params = reason_params.strip().split(",", 1)
                recommendations.append({"tool": tool, "reason": reason.strip(), "params": params.strip()})
        return recommendations