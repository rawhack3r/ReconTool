import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
from core.error_handler import ErrorHandler

class ZeroDayScanner:
    def __init__(self):
        try:
            self.model = IsolationForest(contamination=0.1, random_state=42)
            self.vectorizer = TfidfVectorizer(max_features=1000)
            self.code_analyzer = pipeline(
                "text-classification", 
                model="microsoft/codebert-base",
                device=-1  # Use CPU
            )
        except Exception as e:
            self.model = None
        self.error_handler = ErrorHandler()
    
    def scan_code(self, code_snippets):
        """Scan code snippets for zero-day vulnerabilities"""
        if not self.model or len(code_snippets) < 10:
            return {
                "status": "insufficient_data",
                "message": "At least 10 code snippets required for accurate analysis"
            }
        
        try:
            # Vectorize code snippets
            X = self.vectorizer.fit_transform(code_snippets).toarray()
            
            # Train model
            self.model.fit(X)
            
            # Predict anomalies
            preds = self.model.predict(X)
            scores = self.model.decision_function(X)
            
            # Process results
            suspicious = []
            for i, (snippet, pred, score) in enumerate(zip(code_snippets, preds, scores)):
                if pred == -1:  # Anomaly
                    try:
                        code_analysis = self.code_analyzer(snippet[:512])[0]
                    except:
                        code_analysis = {"label": "UNKNOWN", "score": 0}
                    
                    suspicious.append({
                        "snippet": snippet[:500] + "..." if len(snippet) > 500 else snippet,
                        "risk_score": int((1 - score) * 100),
                        "indicators": self._detect_indicators(snippet),
                        "code_analysis": code_analysis
                    })
            
            return {
                "suspicious_patterns": suspicious,
                "confidence_score": len(suspicious) / len(code_snippets),
                "recommended_actions": [
                    "Review memory management patterns",
                    "Check for unusual system calls",
                    "Verify input validation",
                    "Audit cryptographic implementations"
                ]
            }
        except Exception as e:
            self.error_handler.handle(
                "ZeroDayScanner",
                f"Scan failed: {str(e)}",
                "ZeroDayDetection",
                recoverable=True
            )
            return {"error": str(e)}
    
    def _detect_indicators(self, code):
        """Detect potential vulnerability indicators"""
        indicators = []
        if "malloc(" in code and "free(" not in code:
            indicators.append("Potential memory leak")
        if "system(" in code:
            indicators.append("System command execution")
        if "strcpy(" in code:
            indicators.append("Unsafe string operation")
        if "rand(" in code and "crypt" in code:
            indicators.append("Weak cryptographic implementation")
        if "eval(" in code:
            indicators.append("Dynamic code evaluation")
        return indicators