
import requests
import re

def extract_js_endpoints(target, output_file):
    try:
        response = requests.get(f"https://{target}", timeout=10)
        js_urls = re.findall(r'src=["\'](.*?\.js)["\']', response.text)
        endpoints = []
        for js_url in js_urls:
            js_content = requests.get(js_url, timeout=10).text
            urls = re.findall(r'[\'"](https?://[^\s\'"]+)', js_content)
            endpoints.extend(urls)
        with open(output_file, "w") as f:
            f.write("\n".join(endpoints))
        return endpoints, ""
    except Exception as e:
        return [], str(e)