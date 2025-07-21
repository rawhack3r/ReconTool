import re
import requests
from urllib.parse import urljoin
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Extract API endpoints from JavaScript files"""
    results = {"endpoints": [], "js_files": []}
    
    try:
        base_url = f"http://{target}"
        
        if progress_callback:
            progress_callback("EndpointExtractor", 20, "Fetching homepage...")
        
        response = requests.get(base_url, timeout=10)
        js_files = re.findall(r'<script src="([^"]+\.js)"', response.text)
        
        if progress_callback:
            progress_callback("EndpointExtractor", 40, f"Found {len(js_files)} JS files")
        
        endpoint_patterns = [
            r'fetch\("(/api/[^"]+)"',
            r'\.get\("(/[^"]+)"',
            r'url:\s*["\'](https?://[^"\']+)["\']',
            r'apiEndpoint:\s*["\']([^"\']+)["\']'
        ]
        
        for js_path in js_files:
            full_url = urljoin(base_url, js_path)
            results["js_files"].append(full_url)
            
            try:
                js_response = requests.get(full_url, timeout=5)
                js_content = js_response.text
                
                for pattern in endpoint_patterns:
                    matches = re.findall(pattern, js_content)
                    for match in matches:
                        # Ensure relative paths are made absolute
                        if match.startswith("/"):
                            endpoint = urljoin(base_url, match)
                        else:
                            endpoint = match
                            
                        if endpoint not in results["endpoints"]:
                            results["endpoints"].append(endpoint)
                            
            except Exception as e:
                ErrorHandler.log_error("EndpointExtractor", f"Error processing {full_url}: {str(e)}", target)
        
        if progress_callback:
            progress_callback("EndpointExtractor", 100, f"Extracted {len(results['endpoints'])} endpoints")
            
    except Exception as e:
        ErrorHandler.log_error("EndpointExtractor", str(e), target)
        raise
        
    return results