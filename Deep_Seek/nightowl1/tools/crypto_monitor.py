import requests
from web3 import Web3

class CryptoMonitor:
    CHAINS = {
        "bitcoin": "https://blockchain.info",
        "ethereum": "https://api.etherscan.io/api",
        "polygon": "https://api.polygonscan.com/api"
    }
    
    def get_address_balance(self, address, chain="ethereum"):
        """Get current balance of cryptocurrency address"""
        if chain == "bitcoin":
            url = f"{self.CHAINS[chain]}/rawaddr/{address}"
            data = requests.get(url).json()
            return data["final_balance"]
        else:
            url = f"{self.CHAINS[chain]}?module=account&action=balance&address={address}"
            data = requests.get(url).json()
            return int(data["result"]) / 10**18
    
    def monitor_for_transactions(self, addresses, chain="ethereum"):
        """Detect recent transactions to addresses"""
        alerts = []
        for address in addresses:
            if chain == "bitcoin":
                url = f"{self.CHAINS[chain]}/rawaddr/{address}"
                data = requests.get(url).json()
                if data["n_tx"] > 0:
                    alerts.append({
                        "address": address,
                        "transactions": data["n_tx"],
                        "total_received": data["total_received"]
                    })
            else:
                url = f"{self.CHAINS[chain]}?module=account&action=txlist&address={address}&sort=desc"
                data = requests.get(url).json()
                if data["result"]:
                    latest = data["result"][0]
                    alerts.append({
                        "address": address,
                        "value": int(latest["value"]) / 10**18,
                        "timestamp": latest["timeStamp"]
                    })
        return alerts
    
    def check_for_malicious(self, address):
        """Check if address is flagged as malicious"""
        try:
            url = f"https://api.gopluslabs.io/api/v1/address_security/{address}?chain_id=1"
            response = requests.get(url, timeout=5)
            data = response.json()
            return data["result"]["malicious_address"] > 0
        except:
            return False