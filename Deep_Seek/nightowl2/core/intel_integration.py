import aiohttp
import os
from core.error_handler import ErrorHandler

class ThreatIntelCollector:
    def __init__(self, config):
        self.config = config
        self.error_handler = ErrorHandler()
    
    async def fetch_otx_intel(self, target):
        """Fetch threat intelligence from AlienVault OTX"""
        api_key = os.getenv("OTX_API_KEY")
        if not api_key:
            return {"error": "OTX_API_KEY not set"}
        
        try:
            url = f"https://otx.alienvault.com/api/v1/indicators/domain/{target}/general"
            headers = {"X-OTX-API-KEY": api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()
                    return {
                        "pulses": data.get("pulse_info", {}).get("pulses", []),
                        "malware": data.get("malware", {}).get("data", [])
                    }
        except Exception as e:
            self.error_handler.handle(
                "ThreatIntel",
                f"OTX error: {str(e)}",
                "Threat Intelligence",
                recoverable=True
            )
            return {"error": f"OTX error: {str(e)}"}
    
    async def fetch_virustotal(self, target):
        """Fetch threat intelligence from VirusTotal"""
        api_key = os.getenv("VT_API_KEY")
        if not api_key:
            return {"error": "VT_API_KEY not set"}
        
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{target}"
            headers = {"x-apikey": api_key}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()
                    attributes = data.get("data", {}).get("attributes", {})
                    return {
                        "reputation": attributes.get("reputation", 0),
                        "last_analysis_stats": attributes.get("last_analysis_stats", {}),
                        "malicious": attributes.get("last_analysis_stats", {}).get("malicious", 0)
                    }
        except Exception as e:
            self.error_handler.handle(
                "ThreatIntel",
                f"VirusTotal error: {str(e)}",
                "Threat Intelligence",
                recoverable=True
            )
            return {"error": f"VirusTotal error: {str(e)}"}