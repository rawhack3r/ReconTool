import re
import json
import os
import yaml
from core.utils import load_patterns

class InfoExtractor:
    def __init__(self):
        self.patterns = load_patterns()
    
    def extract_all(self, content, target):
        """Extract all types of information from content"""
        results = {}
        for category, pattern in self.patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Handle tuple matches (like API keys)
                if isinstance(matches[0], tuple):
                    results[category] = [match[1] for match in matches if match[1]]
                else:
                    results[category] = list(set(matches))
        return results
    
    def save_results(self, results, target):
        """Save extracted information to categorized files"""
        output_dir = "outputs/important"
        os.makedirs(output_dir, exist_ok=True)
        
        for category, items in results.items():
            if items:
                file_path = os.path.join(output_dir, f"{category}_{target}.txt")
                with open(file_path, "w") as f:
                    f.write("\n".join(items))
        
        return output_dir