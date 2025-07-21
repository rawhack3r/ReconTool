def get_workflow(mode, custom_tools=None):
    """Enhanced workflow with conditional execution"""
    # ... existing code ...
    
    if mode == "deeper":
        workflow.append({
            "name": "Cloud Infrastructure Mapping",
            "description": "Discover cloud assets and configurations",
            "tools": [{"name": "cloud_scanner", "critical": True}],
            "conditions": lambda r: any(
                t in r.get('subdomains', {}) 
                for t in ['amass', 'sublist3r']
            )
        })
        workflow.append({
            "name": "Dark Web Presence Check",
            "description": "Monitor dark web for target mentions",
            "tools": [{"name": "darkweb_monitor"}],
            "conditions": lambda r: "sensitive_domains" in r
        })
    
    # Add correlation phase
    workflow.append({
        "name": "Threat Correlation",
        "description": "Analyze relationships between entities",
        "tools": [{"name": "correlation_engine"}]
    })
    
    return workflow