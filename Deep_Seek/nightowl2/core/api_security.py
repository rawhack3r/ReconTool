import aiohttp
import json
from core.error_handler import ErrorHandler

class APISecurityTester:
    def __init__(self, config):
        self.config = config
        self.error_handler = ErrorHandler()
    
    async def test_api_security(self, target):
        """Perform API security testing"""
        try:
            endpoints = await self.discover_api_endpoints(target)
            issues = []
            
            for endpoint in endpoints:
                # Test for common vulnerabilities
                if await self.test_bola_vulnerability(endpoint):
                    issues.append({
                        "endpoint": endpoint,
                        "issue": "BOLA Vulnerability",
                        "severity": "High"
                    })
                
                if await self.test_sqli_vulnerability(endpoint):
                    issues.append({
                        "endpoint": endpoint,
                        "issue": "SQL Injection Potential",
                        "severity": "Critical"
                    })
                
                if await self.test_data_exposure(endpoint):
                    issues.append({
                        "endpoint": endpoint,
                        "issue": "Excessive Data Exposure",
                        "severity": "Medium"
                    })
            
            return {
                "endpoints": endpoints,
                "issues": issues,
                "scan_status": "completed"
            }
        except Exception as e:
            self.error_handler.handle(
                "APISecurityTester",
                str(e),
                "API Security",
                recoverable=True
            )
            return {
                "endpoints": [],
                "issues": [],
                "scan_status": "failed",
                "error": str(e)
            }
    
    async def discover_api_endpoints(self, target):
        """Discover API endpoints"""
        try:
            api_url = f"https://{target}/api"
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Simple pattern matching for API endpoints
                        endpoints = re.findall(rf'"{api_url}([^"]+)"', content)
                        return list(set(endpoints))
            return []
        except Exception as e:
            self.error_handler.handle(
                "APISecurityTester",
                f"Endpoint discovery failed: {str(e)}",
                "API Security",
                recoverable=True
            )
            return []
    
    async def test_bola_vulnerability(self, endpoint):
        """Test for Broken Object Level Authorization"""
        test_url = f"{endpoint}/1"
        test_url2 = f"{endpoint}/2"
        try:
            async with aiohttp.ClientSession() as session:
                # Get normal response
                async with session.get(test_url) as response:
                    if response.status != 200:
                        return False
                    data1 = await response.json()
                
                # Try accessing another user's resource
                async with session.get(test_url2) as response:
                    if response.status == 200:
                        data2 = await response.json()
                        if data1 == data2:
                            return True
            return False
        except:
            return False
    
    async def test_sqli_vulnerability(self, endpoint):
        """Test for SQL Injection vulnerability"""
        test_url = f"{endpoint}?id=1'"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url) as response:
                    content = await response.text()
                    if "sql" in content.lower() or "syntax" in content.lower():
                        return True
            return False
        except:
            return False
    
    async def test_data_exposure(self, endpoint):
        """Test for Excessive Data Exposure"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict):
                            if len(data) > 20:  # Too many fields
                                return True
                            if any(key in data for key in ["password", "token", "secret"]):
                                return True
            return False
        except:
            return False