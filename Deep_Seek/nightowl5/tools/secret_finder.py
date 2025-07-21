import re
from core.utils import entropy

class SecretFinder:
    def __init__(self):
        self.patterns = {
            "api_key": r'(?i)(api|key|token|secret)[_-]?key["\']?s*[:=]s*["\']?([a-z0-9]{20,40})["\']?',
            "aws_key": r'(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])',
            "crypto_wallet": r'(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}|0x[a-fA-F0-9]{40}'
        }
    
    def find_secrets(self, text):
        """Find secrets using pattern matching and entropy analysis"""
        results = {}
        
        # Pattern-based detection
        for secret_type, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                results[secret_type] = list(set(matches))
        
        # Entropy-based detection
        high_entropy = self.detect_by_entropy(text)
        if high_entropy:
            results["high_entropy"] = high_entropy
        
        return results
    
    def detect_by_entropy(self, text, threshold=4.5):
        """Detect potential secrets using entropy analysis"""
        words = re.findall(r'\S{20,}', text)
        return [word for word in words if entropy(word) > threshold]