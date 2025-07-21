import os
import time
import random
from core.utils import create_directory, run_command, http_request
from core.error_handler import ErrorHandler

class ContentDiscoverer:
    def __init__(self, target, mode, output_dir, error_handler):
        self.target = target
        self.mode = mode
        self.output_dir = output_dir
        self.error_handler = error_handler
        self.content_dir = os.path.join(output_dir, "content")
        create_directory(self.content_dir)
    
    def run(self, subdomains):
        try:
            results = {
                'urls': [],
                'js_files': [],
                'extensions': [],
                'sensitive_files': []
            }
            
            # 1. Crawl live subdomains
            results['urls'] = self._crawl_subdomains(subdomains)
            
            # 2. JavaScript file analysis
            results['js_files'] = self._analyze_js_files(results['urls'])
            
            # 3. Sensitive file discovery
            results['sensitive_files'] = self._find_sensitive_files(subdomains)
            
            # 4. Extension-based discovery
            results['extensions'] = self._find_special_extensions(results['urls'])
            
            # 5. Wayback machine analysis (deep mode)
            if self.mode == "deep":
                wayback_data = self._query_wayback_machine()
                results['urls'].extend(wayback_data)
                results['urls'] = list(set(results['urls']))
            
            # Save results
            self._save_results(results)
            return results
            
        except Exception as e:
            return self.error_handler.handle_exception(e, "content_discovery", self.target)
    
    def _crawl_subdomains(self, subdomains):
        urls = []
        try:
            # Simulate crawling
            for sub in subdomains[:10]:  # Limit for simulation
                urls.append(f"http://{sub}/")
                urls.append(f"http://{sub}/login")
                urls.append(f"http://{sub}/admin")
                urls.append(f"http://{sub}/api")
                time.sleep(0.1)
            return urls
        except Exception as e:
            self.error_handler.log_error(e, "crawling", self.target)
            return []
    
    def _analyze_js_files(self, urls):
        js_files = []
        try:
            # Simulate JS analysis
            for url in urls[:5]:  # Limit for simulation
                if ".js" in url:
                    js_files.append(url)
                else:
                    # Simulate finding JS files in HTML
                    js_files.append(url + "app.js")
                    js_files.append(url + "main.js")
                    time.sleep(0.05)
            return js_files
        except Exception as e:
            self.error_handler.log_error(e, "js_analysis", self.target)
            return []
    
    def _find_sensitive_files(self, subdomains):
        sensitive_files = []
        try:
            # Simulate sensitive file discovery
            common_files = [
                "/.env", "/.git/config", "/.htaccess", 
                "/web.config", "/robots.txt", "/sitemap.xml"
            ]
            for sub in subdomains[:5]:  # Limit for simulation
                for file in common_files:
                    sensitive_files.append(f"http://{sub}{file}")
                    time.sleep(0.03)
            return sensitive_files
        except Exception as e:
            self.error_handler.log_error(e, "sensitive_files", self.target)
            return []
    
    def _find_special_extensions(self, urls):
        extensions = []
        try:
            # Simulate extension discovery
            ext_types = [".pdf", ".doc", ".xls", ".zip", ".bak", ".sql", ".log"]
            for url in urls[:10]:  # Limit for simulation
                for ext in ext_types:
                    if ext in url:
                        extensions.append(url)
                    else:
                        # Simulate finding new extensions
                        if random.random() > 0.8:
                            new_url = url + "backup" + ext
                            extensions.append(new_url)
                time.sleep(0.05)
            return extensions
        except Exception as e:
            self.error_handler.log_error(e, "extension_discovery", self.target)
            return []
    
    def _query_wayback_machine(self):
        try:
            # Simulate Wayback Machine query
            return [
                f"http://web.archive.org/web/202001/{self.target}/old-page",
                f"http://web.archive.org/web/202101/{self.target}/deprecated"
            ]
        except Exception as e:
            self.error_handler.log_error(e, "wayback_machine", self.target)
            return []
    
    def _save_results(self, results):
        try:
            # Save URLs
            with open(os.path.join(self.content_dir, "urls.txt"), "w") as f:
                f.write("\n".join(results['urls']))
            
            # Save JS files
            with open(os.path.join(self.content_dir, "js_files.txt"), "w") as f:
                f.write("\n".join(results['js_files']))
            
            # Save sensitive files
            with open(os.path.join(self.content_dir, "sensitive_files.txt"), "w") as f:
                f.write("\n".join(results['sensitive_files']))
            
            # Save extensions
            with open(os.path.join(self.content_dir, "extensions.txt"), "w") as f:
                f.write("\n".join(results['extensions']))
        except Exception as e:
            self.error_handler.log_error(e, "content_saving", self.target)