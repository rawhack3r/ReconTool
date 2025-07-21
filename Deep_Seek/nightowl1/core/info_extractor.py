import re
import json
import os

class InfoExtractor:
    def __init__(self):
        self.patterns = {
            "emails": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phones": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "names": r"(?:Mr\.|Mrs\.|Ms\.|Dr\.)?\s*[A-Z][a-z]+\s+[A-Z][a-z]+",
            "api_keys": r"(?i)(key|api|token|secret)[\s:=]['\"]?([a-zA-Z0-9]{20,40})['\"]?",
            "important_paths": r"(admin|backup|config|secret|token|api|internal)",
            "juicy_files": r"(password|backup|dump|secret|conf|config|\.bak|\.old|\.sql)"
        }
    
    def extract_all_important_info(self, results):
        """Extract and categorize all important information"""
        combined = {
            "emails": [],
            "phones": [],
            "names": [],
            "credentials": [],
            "api_keys": [],
            "important_paths": [],
            "juicy_files": []
        }
        
        # Process all text content from results
        for phase, tools in results.items():
            for tool, data in tools.items():
                content = json.dumps(data.get('result', {}))
                self._extract_from_content(content, combined)
        
        # Save categorized output
        self._save_categorized_output(combined)
        return combined
    
    def _extract_from_content(self, content, combined):
        """Extract patterns from content"""
        for category, pattern in self.patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                # Handle tuple matches (like API keys)
                if isinstance(matches[0], tuple):
                    for match in matches:
                        if match[1]:  # Only add if second part exists
                            combined[category].append(match[1])
                else:
                    combined[category].extend(matches)
    
    def _save_categorized_output(self, data):
        """Save categorized findings to files"""
        for category, items in data.items():
            if items:
                with open(f"outputs/important/{category}.txt", "w") as f:
                    f.write("\n".join(set(items)))
    
    def identify_important_emails(self, emails):
        """Categorize emails by importance"""
        important = []
        regular = []
        
        for email in emails:
            if any(keyword in email for keyword in 
                   ["admin", "root", "support", "security", "finance"]):
                important.append(email)
            else:
                regular.append(email)
        
        return {
            "important": important,
            "regular": regular
        }