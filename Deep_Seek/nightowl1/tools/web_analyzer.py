import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from core.error_handler import ErrorHandler

def run(target, progress_callback=None):
    """Analyze website content for important information"""
    results = {
        "emails": [],
        "phones": [],
        "names": [],
        "technologies": [],
        "social_links": []
    }
    
    # Get home page
    base_url = f"http://{target}"
    
    try:
        if progress_callback:
            progress_callback("web_analyzer", 20, f"Fetching {base_url}")
        
        response = requests.get(base_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract emails
        results["emails"] = _extract_emails(response.text, target)
        
        # Extract phones
        results["phones"] = _extract_phones(response.text)
        
        # Extract names (from author meta tags or footer)
        results["names"] = _extract_names(soup)
        
        # Detect technologies
        results["technologies"] = _detect_technologies(response.headers, soup)
        
        # Find social links
        results["social_links"] = _find_social_links(soup, base_url)
        
    except Exception as e:
        ErrorHandler.log_error("web_analyzer", str(e), target)
    
    return results

def _extract_emails(content, domain):
    """Extract emails from text content"""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, content)
    return [email for email in emails if domain in email]

def _extract_phones(content):
    """Extract phone numbers from text content"""
    phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    return re.findall(phone_pattern, content)

def _extract_names(soup):
    """Extract potential names from page content"""
    # Check meta author tag
    author_tag = soup.find('meta', attrs={'name': 'author'})
    if author_tag and author_tag.get('content'):
        return [author_tag['content']]
    
    # Check footer for names
    names = []
    footer = soup.find('footer')
    if footer:
        # Simple heuristic for names in footer
        for item in footer.find_all('div'):
            text = item.get_text().strip()
            if re.match(r"^[A-Z][a-z]+ [A-Z][a-z]+$", text):
                names.append(text)
    
    return names

def _detect_technologies(headers, soup):
    """Detect web technologies from headers and meta tags"""
    tech = []
    
    # Server header
    server = headers.get('Server', '')
    if server:
        tech.append(f"Server: {server}")
    
    # X-Powered-By header
    powered_by = headers.get('X-Powered-By', '')
    if powered_by:
        tech.append(f"Powered By: {powered_by}")
    
    # Meta generator tag
    generator_tag = soup.find('meta', attrs={'name': 'generator'})
    if generator_tag and generator_tag.get('content'):
        tech.append(f"Generator: {generator_tag['content']}")
    
    return tech

def _find_social_links(soup, base_url):
    """Find social media links on the page"""
    social_platforms = [
        "facebook.com", "twitter.com", "linkedin.com",
        "instagram.com", "youtube.com", "github.com"
    ]
    
    social_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if any(platform in full_url for platform in social_platforms):
            social_links.append(full_url)
    
    return social_links