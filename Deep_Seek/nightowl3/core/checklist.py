def generate_manual_checklist(state):
    checklist = """
    NightOwl Manual Testing Checklist
    =================================
    
    Critical Areas to Verify:
    1. Authentication Flows
       - Test for weak password policies
       - Check for 2FA bypass techniques
       - Verify session management security
    
    2. Sensitive Data Exposure
       - Check for PII in client-side storage
       - Verify proper encryption of sensitive data
       - Test for information leakage in error messages
    
    3. Injection Vulnerabilities
       - Test all input fields for SQLi
       - Verify command injection vectors
       - Check for XXE vulnerabilities
    
    4. Business Logic Flaws
       - Test for price manipulation
       - Verify access control bypasses
       - Check for workflow circumvention
    
    Domains Requiring Special Attention:
    """
    
    if "live_urls" in state:
        important = [url for url in state["live_urls"] if any(kw in url for kw in ["admin", "api", "internal"])]
        for url in important[:10]:  # Top 10 important URLs
            checklist += f"    - {url}\n"
    
    return checklist