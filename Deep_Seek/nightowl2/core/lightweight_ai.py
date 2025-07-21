import re
import random
from core.error_handler import ErrorHandler

class LightweightAI:
    TOOL_KNOWLEDGE_BASE = {
        "subdomain": ["amass", "sublist3r", "assetfinder", "findomain", "crt_sh", "subbrute"],
        "api": ["api_security", "endpoint_extractor", "api_sequences"],
        "cloud": ["cloud_scanner", "asset_discovery"],
        "secret": ["secret_finder", "github_secret_scanner"],
        "content": ["content_discovery", "dynamic_crawler"],
        "vuln": ["nuclei_wrapper", "zap_api", "vulnerability_scanner"],
        "osint": ["web_analyzer", "darkweb_intel", "hackerone_scoper"],
    }

    KEYWORD_TRIGGERS = {
        "subdomain": ["domain", "subdomain", "dns", "host", "resolve"],
        "api": ["api", "endpoint", "rest", "graphql", "swagger"],
        "cloud": ["aws", "azure", "gcp", "cloud", "s3", "bucket"],
        "secret": ["secret", "key", "credential", "token", "password"],
        "content": ["dir", "path", "file", "discover", "url"],
        "vuln": ["vulnerability", "scan", "xss", "sql", "secure"],
        "osint": ["osint", "darkweb", "hackerone", "scope"],
    }

    def recommend_tools(self, target_description):
        """Recommend tools based on keyword matching in target description"""
        try:
            # Clean and normalize the description
            clean_text = re.sub(r'[^\w\s]', '', target_description.lower())
            words = clean_text.split()
            
            # Count keyword matches
            category_scores = {category: 0 for category in self.TOOL_KNOWLEDGE_BASE}
            for word in words:
                for category, triggers in self.KEYWORD_TRIGGERS.items():
                    if word in triggers:
                        category_scores[category] += 1
            
            # Get top 2 categories
            top_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            
            # Select tools from top categories
            recommended = []
            for category, score in top_categories:
                if score > 0:
                    recommended.extend(self.TOOL_KNOWLEDGE_BASE[category])
            
            return list(set(recommended)) if recommended else self.default_recommendations()
        
        except Exception as e:
            ErrorHandler.log_error("LightweightAI", str(e), "recommendation")
            return self.default_recommendations()
    
    def default_recommendations(self):
        """Fallback recommendations"""
        return ["amass", "nuclei_wrapper", "secret_finder", "content_discovery"]