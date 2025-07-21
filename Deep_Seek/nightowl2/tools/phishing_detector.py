import requests
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from core.error_handler import ErrorHandler

class PhishingDetector:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        self.error_handler = ErrorHandler()
        self.threshold = 0.85
    
    def detect_clones(self, target_domain, subdomains):
        """Detect phishing clones of the target domain"""
        results = {}
        try:
            main_embedding = self._get_embedding(f"https://{target_domain}")
            
            for subdomain in subdomains:
                try:
                    sub_embedding = self._get_embedding(f"https://{subdomain}")
                    similarity = cosine_similarity(
                        [main_embedding], 
                        [sub_embedding]
                    )[0][0]
                    
                    if similarity > self.threshold:
                        results[subdomain] = {
                            "similarity": similarity,
                            "phishing_risk": min(100, int(similarity * 100)),
                            "recommendations": [
                                "Check for typosquatting",
                                "Verify SSL certificate",
                                "Investigate domain registration"
                            ]
                        }
                except Exception as e:
                    self.error_handler.handle(
                        "PhishingDetector",
                        f"Subdomain {subdomain} analysis failed: {str(e)}",
                        "PhishingDetection",
                        recoverable=True
                    )
        except Exception as e:
            self.error_handler.handle(
                "PhishingDetector",
                f"Main domain analysis failed: {str(e)}",
                "PhishingDetection",
                recoverable=True
            )
        return results
    
    def _get_embedding(self, url):
        """Get embedding for a URL's content"""
        try:
            response = requests.get(url, timeout=10, verify=False)
            content = response.text[:5000]  # First 5000 characters
            return self.model.encode([content])[0]
        except Exception as e:
            # Fallback to domain name embedding
            return self.model.encode([url])[0]