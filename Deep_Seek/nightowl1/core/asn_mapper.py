import requests
from collections import defaultdict

class ASNMapper:
    def __init__(self):
        self.cache = {}
    
    def get_asn_details(self, asn):
        """Get ASN details with caching"""
        if asn in self.cache:
            return self.cache[asn]
        
        try:
            url = f"https://api.bgpview.io/asn/{asn}"
            response = requests.get(url, timeout=5)
            data = response.json()
            details = {
                "asn": asn,
                "name": data["data"]["name"],
                "description": data["data"]["description_short"],
                "country": data["data"]["country_code"],
                "rir": data["data"]["rir_name"]
            }
            self.cache[asn] = details
            return details
        except:
            return {"asn": asn, "error": "API failure"}
    
    def map_ip_to_asn(self, ip):
        """Map IP address to ASN"""
        try:
            url = f"https://api.bgpview.io/ip/{ip}"
            response = requests.get(url, timeout=3)
            data = response.json()
            return data["data"]["prefixes"][0]["asn"]["asn"]
        except:
            return None
    
    def build_network_map(self, ips):
        """Create ASN network topology"""
        asn_map = defaultdict(list)
        for ip in ips:
            asn = self.map_ip_to_asn(ip)
            if asn:
                asn_map[asn].append(ip)
        
        return [
            {"asn": asn, "details": self.get_asn_details(asn), "ips": ips}
            for asn, ips in asn_map.items()
        ]