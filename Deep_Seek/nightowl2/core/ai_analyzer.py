import openai
from transformers import pipeline
import asyncio
import re
from core.error_handler import ErrorHandler

class AIAnalyzer:
    def __init__(self, config):
        self.config = config
        self.openai_api_key = config.get("OPENAI_API_KEY")
        self.classifier = pipeline(
            "text-classification", 
            model="distilbert-base-uncased",
            device=-1  # Use CPU
        )
        self.error_handler = ErrorHandler()
    
    async def analyze_results(self, target, results):
        """Perform AI-powered analysis of recon data"""
        insights = {
            "vulnerability_analysis": "",
            "secret_classification": [],
            "attack_paths": "",
            "findings": []
        }
        
        try:
            # 1. Vulnerability analysis
            vuln_data = self._extract_vulnerability_data(results)
            if vuln_data:
                vuln_analysis = await self._analyze_vulnerabilities(target, vuln_data)
                insights["vulnerability_analysis"] = vuln_analysis
                insights["findings"].append({
                    "title": "Vulnerability Analysis",
                    "description": vuln_analysis,
                    "confidence": 85,
                    "recommendations": "Prioritize critical vulnerabilities for immediate remediation"
                })
            
            # 2. Secret classification
            secret_data = self._extract_secret_data(results)
            if secret_data:
                secret_classification = self._classify_secrets(secret_data)
                insights["secret_classification"] = secret_classification
                insights["findings"].append({
                    "title": "Secret Exposure",
                    "description": f"Found {len(secret_classification)} potential secrets",
                    "confidence": 92,
                    "recommendations": "Rotate all exposed credentials immediately"
                })
            
            # 3. Attack path modeling
            asset_data = self._extract_asset_data(results)
            if asset_data:
                attack_paths = await self._model_attack_paths(target, asset_data)
                insights["attack_paths"] = attack_paths
                insights["findings"].append({
                    "title": "Attack Path Analysis",
                    "description": attack_paths,
                    "confidence": 78,
                    "recommendations": "Harden perimeter security and implement WAF rules"
                })
        except Exception as e:
            self.error_handler.handle(
                "AIAnalyzer",
                f"Analysis failed: {str(e)}",
                "AI Analysis",
                recoverable=True
            )
        
        return insights
    
    async def _analyze_vulnerabilities(self, target, vuln_data):
        """Analyze vulnerabilities using AI"""
        if not self.openai_api_key:
            return "OpenAI API key not configured"
        
        try:
            prompt = f"""
            Analyze these vulnerability findings for {target}:
            {vuln_data[:3000]}
            
            Identify:
            1. Critical attack vectors
            2. Potential business impact
            3. Recommended remediation steps
            
            Format response with clear headings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                api_key=self.openai_api_key
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"AI analysis failed: {str(e)}"
    
    def _classify_secrets(self, secret_data):
        """Classify secrets using NLP model"""
        try:
            classifications = []
            for secret in secret_data[:50]:  # Limit to first 50 secrets
                result = self.classifier(secret)
                if result[0]['score'] > 0.85:
                    classifications.append({
                        "secret": secret[:50] + "..." if len(secret) > 50 else secret,
                        "label": result[0]['label'],
                        "score": result[0]['score']
                    })
            return classifications
        except Exception as e:
            self.error_handler.handle(
                "AIAnalyzer",
                f"Secret classification failed: {str(e)}",
                "AI Analysis",
                recoverable=True
            )
            return []
    
    async def _model_attack_paths(self, target, asset_data):
        """Model attack paths using AI"""
        if not self.openai_api_key:
            return "OpenAI API key not configured"
        
        try:
            prompt = f"""
            Based on these assets for {target}:
            {asset_data[:3000]}
            
            Model potential attack paths considering:
            1. Perimeter weaknesses
            2. Cloud misconfigurations
            3. Sensitive data exposure
            
            Provide the top 3 attack paths in markdown format.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                api_key=self.openai_api_key
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Attack modeling failed: {str(e)}"
    
    def _extract_vulnerability_data(self, results):
        """Extract vulnerability data from results"""
        vulns = results.get("vulnerabilities", {})
        return "\n".join([f"{tool}: {data}" for tool, data in vulns.items()])
    
    def _extract_secret_data(self, results):
        """Extract secret data from results"""
        secrets = results.get("information", {}).get("secrets", [])
        return secrets[:100]  # Limit to 100 secrets
    
    def _extract_asset_data(self, results):
        """Extract asset data from results"""
        assets = results.get("subdomains", {})
        cloud = results.get("cloud", {})
        return f"Subdomains: {assets}\nCloud Resources: {cloud}"