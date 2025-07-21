import re
import yaml
import os
from tools.email_extractor import extract_emails
from tools.secret_finder import SecretFinder
from core.error_handler import ErrorHandler

class InfoExtractor:
    def __init__(self):
        self.patterns = self._load_patterns()
        self.secret_finder = SecretFinder()
        self.error_handler = ErrorHandler()
    
    def extract_all(self, content):
        """Extract all types of information from content"""
        results = {}
        
        # Extract using predefined patterns
        for category, pattern in self.patterns.items():
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    results[category] = list(set(matches))
            except Exception as e:
                self.error_handler.handle(
                    "InfoExtractor",
                    f"Pattern extraction failed for {category}: {str(e)}",
                    "InformationExtraction",
                    recoverable=True
                )
        
        # Extract emails
        try:
            emails = extract_emails(content)
            if emails:
                results["emails"] = emails
        except Exception as e:
            self.error_handler.handle(
                "InfoExtractor",
                f"Email extraction failed: {str(e)}",
                "InformationExtraction",
                recoverable=True
            )
        
        # Find secrets
        try:
            secrets = self.secret_finder.find_secrets(content)
            if secrets:
                results["secrets"] = secrets
        except Exception as e:
            self.error_handler.handle(
                "InfoExtractor",
                f"Secret finding failed: {str(e)}",
                "InformationExtraction",
                recoverable=True
            )
        
        return results
    
    def save_results(self, results, target, output_dir="outputs/important"):
        """Save extracted information to categorized files"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            for category, items in results.items():
                if items:
                    file_path = os.path.join(output_dir, f"{category}_{target}.txt")
                    with open(file_path, "w") as f:
                        if isinstance(items, dict):
                            for key, value in items.items():
                                f.write(f"{key}: {value}\n")
                        else:
                            f.write("\n".join(items))
        except Exception as e:
            self.error_handler.handle(
                "InfoExtractor",
                f"Result saving failed: {str(e)}",
                "InformationExtraction",
                recoverable=True
            )
    
    def _load_patterns(self):
        """Load extraction patterns from YAML file"""
        try:
            with open("config/patterns.yaml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.error_handler.handle(
                "InfoExtractor",
                f"Pattern loading failed: {str(e)}",
                "InformationExtraction",
                recoverable=True
            )
            # Return default patterns
            return {
                "phone_numbers": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                "names": r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',
                "ip_addresses": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
                "important_paths": r'\b(admin|backup|config|secret|internal|dashboard)\b',
                "juicy_files": r'\.(bak|old|sql|backup|conf|config|env|swp)\b'
            }