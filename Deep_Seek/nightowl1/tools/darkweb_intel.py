import requests
import os
import re
from stem import Signal
from stem.control import Controller
from datetime import datetime
from core.error_handler import ErrorHandler

class DarkWebMonitor:
    def __init__(self):
        self.session = self.create_tor_session()
        self.controller = self.connect_controller()
        self.markets = self.load_market_list()
        self.forums = self.load_forum_list()
    
    def create_tor_session(self):
        session = requests.Session()
        session.proxies = {
            'http': 'socks5h://localhost:9050',
            'https': 'socks5h://localhost:9050'
        }
        return session
    
    def connect_controller(self):
        try:
            controller = Controller.from_port(port=9051)
            controller.authenticate(password=os.getenv("TOR_PASSWORD", "nightowl"))
            return controller
        except Exception as e:
            ErrorHandler.log_error("DarkWeb", f"Tor control error: {str(e)}", "system")
            return None
    
    def renew_identity(self):
        if self.controller:
            self.controller.signal(Signal.NEWNYM)
    
    def load_market_list(self):
        return [
            "http://darkmarketxyz.onion",
            "http://blackbankmarkets.onion"
        ]
    
    def load_forum_list(self):
        return [
            "http://darkforumzzz.onion",
            "http://breachtalk.onion"
        ]
    
    def search_market_listings(self, target):
        results = []
        for market in self.markets:
            try:
                search_url = f"{market}/search?q={target}"
                response = self.session.get(search_url, timeout=30)
                if response.status_code == 200:
                    listings = self.extract_listings(response.text)
                    results.append({
                        "market": market,
                        "listings": listings,
                        "count": len(listings)
                    })
                self.renew_identity()
            except Exception as e:
                ErrorHandler.log_error("DarkWeb", f"Market error: {str(e)}", market)
        return results
    
    def search_forum_mentions(self, target):
        results = []
        for forum in self.forums:
            try:
                search_url = f"{forum}/search?query={target}"
                response = self.session.get(search_url, timeout=30)
                if response.status_code == 200:
                    mentions = self.extract_mentions(response.text, target)
                    results.append({
                        "forum": forum,
                        "mentions": mentions,
                        "count": len(mentions)
                    })
                self.renew_identity()
            except Exception as e:
                ErrorHandler.log_error("DarkWeb", f"Forum error: {str(e)}", forum)
        return results
    
    def extract_listings(self, html):
        pattern = re.compile(r'<div class="listing">(.*?)</div>', re.DOTALL)
        return pattern.findall(html)[:3]
    
    def extract_mentions(self, text, target):
        pattern = re.compile(fr"([^.]*?{target}[^.]*\.)", re.IGNORECASE)
        return pattern.findall(text)

def run(target, progress_callback=None):
    monitor = DarkWebMonitor()
    results = {
        "market_listings": [],
        "forum_mentions": []
    }
    
    try:
        if progress_callback:
            progress_callback("DarkWeb", 30, "Searching dark markets...")
        results["market_listings"] = monitor.search_market_listings(target)
        
        if progress_callback:
            progress_callback("DarkWeb", 60, "Scanning forums...")
        results["forum_mentions"] = monitor.search_forum_mentions(target)
        
        if progress_callback:
            progress_callback("DarkWeb", 100, "Dark web scan completed")
            
    except Exception as e:
        ErrorHandler.log_error("DarkWeb", str(e), target)
        raise
        
    return results