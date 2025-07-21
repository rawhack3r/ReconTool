def render_html_report(scan_results, summary_stats):
    # Example; you should style this further
    html = "<html><head><title>NightOwl Report</title></head><body>"
    html += "<h1>NightOwl Reconnaissance Summary</h1>"
    html += "<h2>Scan Summary</h2><ul>"
    for k, v in summary_stats.get('results', {}).items():
        html += f"<li>{k}: <strong>{v}</strong></li>"
    html += "</ul><h2>Tool Results</h2>"
    for tool, res in scan_results.items():
        html += f"<h3>{tool}</h3><ul>"
        html += f"<li>Status: {res.status}</li>"
        html += f"<li>Duration: {res.duration}</li>"
        html += f"<li>Results: {len(res.results)}</li>"
        if res.errors:
            html += f"<li style='color:red'>Errors: {'; '.join(res.errors)}</li>"
        html += "</ul><hr>"
    html += "</body></html>"
    return html
