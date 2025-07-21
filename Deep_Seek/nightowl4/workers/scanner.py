import time
import os
import json
import requests
from core.distributed import DistributedScanner
from core.utils import NightOwlUtils

utils = NightOwlUtils()

def worker_process():
    scanner = DistributedScanner()
    print("[*] NightOwl worker started. Waiting for tasks...")
    
    while True:
        task = scanner.get_task()
        if not task:
            time.sleep(5)
            continue
        
        print(f"[*] Processing {task['type']} task for {task['target']}")
        
        result = None
        try:
            if task["type"] == "subdomain_enum":
                result = run_subdomain_enum(task["target"])
            elif task["type"] == "vuln_scan":
                result = run_vuln_scan(task["target"])
            elif task["type"] == "content_discovery":
                result = run_content_discovery(task["target"])
            
            scanner.send_result(task, {"status": "success", "result": result})
            print(f"[+] Task completed: {task['type']} for {task['target']}")
        except Exception as e:
            scanner.send_result(task, {"status": "error", "error": str(e)})
            print(f"[!] Task failed: {task['type']} for {task['target']}: {str(e)}")

def run_subdomain_enum(target):
    tools = ["amass", "subfinder", "assetfinder"]
    results = []
    for tool in tools:
        if tool == "amass":
            cmd = f"amass enum -passive -d {target} -o /dev/stdout"
        elif tool == "subfinder":
            cmd = f"subfinder -d {target} -silent"
        elif tool == "assetfinder":
            cmd = f"assetfinder -subs-only {target}"
        
        result = utils.run_command(cmd)
        if result and not result.startswith("Error"):
            results.extend(result.splitlines())
    
    return list(set(results))

def run_vuln_scan(target):
    cmd = f"nuclei -u {target} -severity medium,high,critical -silent"
    result = utils.run_command(cmd)
    return result.splitlines() if result else []

def run_content_discovery(target):
    cmd = f"gospider -s https://{target} -d 2 -t 50 -c 5 --other-source --subs -o output"
    utils.run_command(cmd)
    
    # Process output files
    results = []
    if os.path.exists("output"):
        for file in os.listdir("output"):
            if file.endswith(".txt"):
                with open(os.path.join("output", file), "r") as f:
                    results.extend(f.readlines())
    
    return results

if __name__ == "__main__":
    worker_process()