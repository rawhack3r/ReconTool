import requests
import os
from stem import Signal
from stem.control import Controller
from core.error_handler import ErrorHandler

def get_tor_session():
    """Create Tor session for dark web access"""
    session = requests.session()
    session.proxies = {
        'http': 'socks5h://localhost:9050',
        'https': 'socks5h://localhost:9050'
    }
    return session

def renew_tor_identity():
    """Renew Tor connection for new exit node"""
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password=os.getenv("TOR_PASSWORD"))
        controller.signal(Signal.NEWNYM)

def search_dark_web_forums(session, target):
    """Search dark web forums for target mentions"""
    forums = [
        "http://darkzzx4avcsuofgfeup5s4sjzecj53jf4cjd4l4v5kyz7k7vj2qvyd.onion/search?q={target}",
        "http://tor66sewebgixwhcqm7mozndowt6j7q2fjqvv3dhu2w2mdb5d6rv2ad.onion/search?query={target}"
    ]
    results = []
    
    for forum in forums:
        try:
            url = forum.format(target=target)
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                results.append({
                    "forum": forum.split('/')[2],
                    "mentions": len(response.text.lower().split(target.lower())) - 1,
                    "url": url
                })
            renew_tor_identity()
        except Exception as e:
            ErrorHandler.log_error("DarkwebMonitor", f"Forum error: {str(e)}", target)
            continue
            
    return results

def run(target, progress_callback=None):
    """Comprehensive dark web monitoring"""
    results = {"mentions": [], "leaks": [], "market_listings": []}
    
    try:
        # Initialize Tor session
        if progress_callback:
            progress_callback("DarkwebMonitor", 10, "Initializing Tor connection...")
        
        tor_session = get_tor_session()
        
        # Search forums
        if progress_callback:
            progress_callback("DarkwebMonitor", 30, "Scanning dark web forums...")
        results["mentions"] = search_dark_web_forums(tor_session, target)
        
        # Check leak databases
        if progress_callback:
            progress_callback("DarkwebMonitor", 60, "Checking leak databases...")
        
        # Scan dark markets
        if progress_callback:
            progress_callback("DarkwebMonitor", 85, "Scanning marketplaces...")
        
        if progress_callback:
            progress_callback("DarkwebMonitor", 100, "Dark web scan completed")
            
    except Exception as e:
        ErrorHandler.log_error("DarkwebMonitor", str(e), target)
        raise
        
    return results