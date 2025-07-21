import re
import os
import requests
import logging
from web3 import Web3
from core.error_handler import ErrorHandler

class BlockchainAnalyzer:
    def __init__(self, config=None):
        self.w3 = Web3()
        self.eth_scan_api = "https://api.etherscan.io/api"
        self.error_handler = ErrorHandler()
        self.config = config or {}
        self.api_key = os.getenv("ETHERSCAN_API_KEY") or self.config.get("ETHERSCAN_API_KEY", "")
        self.logger = logging.getLogger("BlockchainAnalyzer")
        
        # Configure logger
        logging.basicConfig(level=logging.INFO)
    
    def scan_blockchain_assets(self, content):
        """Scan content for blockchain-related assets"""
        addresses = self._find_crypto_addresses(content)
        results = {}
        
        for address in addresses:
            try:
                asset_type = self._identify_asset_type(address)
                if not asset_type:
                    continue
                    
                if asset_type == "ETH":
                    balance = self._get_eth_balance(address)
                    txs = self._get_transaction_count(address)
                    risk = self._calculate_risk(balance, txs)
                    
                    results[address] = {
                        "type": asset_type,
                        "balance": balance,
                        "transactions": txs,
                        "risk_score": risk
                    }
                else:
                    # Placeholder for other blockchain types
                    results[address] = {
                        "type": asset_type,
                        "balance": 0,
                        "transactions": 0,
                        "risk_score": 30,
                        "warning": "Analysis not implemented for this blockchain"
                    }
            except Exception as e:
                self.error_handler.handle(
                    "BlockchainAnalyzer",
                    f"Error analyzing {address}: {str(e)}",
                    "BlockchainAnalysis",
                    recoverable=True
                )
                continue
        
        return results
    
    def _identify_asset_type(self, address):
        """Identify the cryptocurrency type based on address pattern"""
        patterns = {
            "ETH": r'^0x[a-fA-F0-9]{40}$',
            "BTC": r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$',
            "BNB": r'^bnb[a-z0-9]{39}$',
            "XRP": r'^r[0-9a-zA-Z]{24,34}$',
            "DOGE": r'^D[0-9a-zA-Z]{33}$',
            "LTC": r'^L[0-9a-zA-Z]{33}$',
            "XLM": r'^G[A-Z0-9]{55}$'
        }
        
        for asset_type, pattern in patterns.items():
            if re.match(pattern, address):
                return asset_type
        return None
    
    def _find_crypto_addresses(self, content):
        """Find cryptocurrency addresses in content"""
        patterns = [
            r'0x[a-fA-F0-9]{40}',  # ETH
            r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',  # BTC
            r'bnb[a-z0-9]{39}',  # BNB
            r'r[0-9a-zA-Z]{24,34}',  # XRP
            r'D[0-9a-zA-Z]{33}',  # DOGE
            r'L[0-9a-zA-Z]{33}',  # LTC
            r'G[A-Z0-9]{55}'  # XLM (corrected pattern)
        ]
        addresses = []
        for pattern in patterns:
            addresses.extend(re.findall(pattern, content))
        return list(set(addresses))
    
    def _get_eth_balance(self, address):
        """Get ETH balance for an address"""
        if not self.api_key:
            self.logger.warning("Etherscan API key not configured. Skipping balance check.")
            return 0
            
        try:
            response = requests.get(
                self.eth_scan_api,
                params={
                    "module": "account",
                    "action": "balance",
                    "address": address,
                    "tag": "latest",
                    "apikey": self.api_key
                },
                timeout=10
            )
            data = response.json()
            
            if data.get("status") != "1":
                error = data.get("message", "Unknown error")
                raise Exception(f"Etherscan API error: {error}")
                
            return int(data.get("result", 0)) / 10**18
        except Exception as e:
            self.error_handler.handle(
                "BlockchainAnalyzer",
                f"ETH balance check failed: {str(e)}",
                "BlockchainAnalysis",
                recoverable=True
            )
            return 0
    
    def _get_transaction_count(self, address):
        """Get transaction count for an address"""
        if not self.api_key:
            self.logger.warning("Etherscan API key not configured. Skipping transaction check.")
            return 0
            
        try:
            response = requests.get(
                self.eth_scan_api,
                params={
                    "module": "account",
                    "action": "txlist",
                    "address": address,
                    "startblock": 0,
                    "endblock": 99999999,
                    "sort": "asc",
                    "apikey": self.api_key
                },
                timeout=15
            )
            data = response.json()
            
            if data.get("status") != "1":
                error = data.get("message", "Unknown error")
                raise Exception(f"Etherscan API error: {error}")
                
            return len(data.get("result", []))
        except Exception as e:
            self.error_handler.handle(
                "BlockchainAnalyzer",
                f"Transaction count failed: {str(e)}",
                "BlockchainAnalysis",
                recoverable=True
            )
            return 0
    
    def _calculate_risk(self, balance, tx_count):
        """Calculate risk score for an address with more nuanced logic"""
        # Base risk based on balance
        if balance > 100: risk = 100
        elif balance > 50: risk = 90
        elif balance > 10: risk = 80
        elif balance > 1: risk = 70
        elif balance > 0.1: risk = 50
        else: risk = 30
        
        # Adjust based on transaction count
        if tx_count > 1000: risk = min(100, risk + 30)
        elif tx_count > 100: risk = min(100, risk + 20)
        elif tx_count > 10: risk = min(100, risk + 10)
        
        # High activity with low balance might indicate scam operations
        if tx_count > 50 and balance < 0.1:
            risk = min(100, risk + 20)
            
        return risk