
import asyncio
import argparse
import sys
import os
import glob
import subprocess
import jinja2
import psutil
import yaml
from datetime import datetime

# Ensure nightowl package is importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from core.orchestrator import NightOwlOrchestrator
    from core.error_handler import ErrorHandler
except ImportError as e:
    print(f"Import error: {e}. Ensure PYTHONPATH includes /home/nightowl/1807/19/Grok/nightowl")
    sys.exit(1)

async def main():
    parser = argparse.ArgumentParser(description="NightOwl Reconnaissance Suite")
    parser.add_argument("--target", required=True, help="Target domain or list file")
    parser.add_argument("--mode", choices=["light", "deep", "deeper", "custom"], default="light", help="Recon mode")
    parser.add_argument("--custom-tools", nargs='*', help="Custom tools for custom mode")
    parser.add_argument("--resume", action="store_true", help="Resume from last state")
    parser.add_argument("--retry-failed", action="store_true", help="Retry failed tools")
    args = parser.parse_args()

    ErrorHandler.setup_logging()
    target_type = "list" if os.path.isfile(args.target) else "single"
    targets = [args.target] if target_type == "single" else open(args.target).read().splitlines()
    
    for target in targets:
        orchestrator = NightOwlOrchestrator(target, args.mode, args.custom_tools)
        if args.resume and os.path.exists(f"output/state_{target}.json"):
            print(f"Resuming scan for {target}...")
        elif args.retry_failed:
            print(f"Retrying failed tools for {target}...")
            await orchestrator.retry_failed_tools()
        else:
            print(f"Starting NightOwl recon for {target} (Mode: {args.mode}, Type: {target_type})")
            await orchestrator.run_workflow()

        # System resource monitoring
        print(f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% | Network: {psutil.net_io_counters().bytes_sent / 1024:.1f} KB/s")

        # Merge outputs
        output_dir = "output"
        final_output = f"{output_dir}/final_{target}.txt"
        tool_outputs = glob.glob(f"{output_dir}/*_{target}.txt")
        results = set()
        for tool_output in tool_outputs:
            try:
                with open(tool_output, 'r') as f:
                    results.update(line.strip() for line in f if line.strip())
            except Exception as e:
                ErrorHandler.log_error(f"Error reading {tool_output}: {e}")

        with open(final_output, 'w') as f:
            for result in sorted(results):
                f.write(f"{result}\n")

        # Live/Dead check
        live_output = f"{output_dir}/live_{target}.txt"
        non_resolved_output = f"{output_dir}/non_resolved_{target}.txt"
        try:
            subprocess.run(["httpx", "-l", final_output, "-o", live_output, "-silent", "-status-code", "-no-color"], check=True)
            resolved = set(open(live_output).read().splitlines())
            with open(non_resolved_output, 'w') as f:
                for result in results:
                    if result not in resolved:
                        f.write(f"{result}\n")
        except Exception as e:
            ErrorHandler.log_error(f"Error running httpx: {e}")

        # Important assets and secrets
        important_output = f"{output_dir}/important_{target}.txt"
        secrets_output = f"{output_dir}/secrets_{target}.txt"
        try:
            subprocess.run(f"gf interesting {live_output} > {important_output}", shell=True, check=True)
            subprocess.run(f"cat output/gf_{target}.txt output/emailhunter_{target}.txt output/theHarvester_{target}.txt > {secrets_output}", shell=True, check=True)
        except Exception as e:
            ErrorHandler.log_error(f"Error extracting important/secrets: {e}")

        # Vulnerabilities
        vulns_output = f"{output_dir}/vulns_{target}.txt"
        try:
            subprocess.run(f"cat output/nuclei_{target}.txt output/zap_{target}.txt output/metasploit_{target}.txt > {vulns_output}", shell=True, check=True)
        except Exception as e:
            ErrorHandler.log_error(f"Error extracting vulnerabilities: {e}")

        # Generate HTML report
        generate_html_report(target, tool_outputs, live_output, non_resolved_output, important_output, secrets_output, vulns_output)

        # Print error summary
        errors = ErrorHandler.get_error_summary()
        if errors:
            print("\nError Summary:")
            for error in errors:
                print(error)
            print("Run with --retry-failed to retry failed tools.")

def generate_html_report(target, tool_outputs, live_output, non_resolved_output, important_output, secrets_output, vulns_output):
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NightOwl Recon Report - {{ target }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f9; }
            h1 { color: #2c3e50; text-align: center; }
            h2, h3 { color: #34495e; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #3498db; color: white; }
            .phase { margin: 20px 0; }
            pre { background-color: #ecf0f1; padding: 10px; border-radius: 5px; }
            .icon { margin-right: 5px; }
        </style>
    </head>
    <body>
        <h1>NightOwl Recon Report - {{ target }}</h1>
        <p>Generated on: {{ timestamp }}</p>
        <p>Total Time: {{ total_time }}</p>
        <h2>Summary</h2>
        <p>Subdomains: {{ subdomain_count }} <span class="icon">🔍</span></p>
        <p>Secrets: {{ secret_count }} <span class="icon">🔒</span></p>
        <p>Vulnerabilities: {{ vuln_count }} <span class="icon">⚠️</span></p>
        {% for phase, results in report.items() %}
        <div class="phase">
            <h2>{{ phase }}</h2>
            <table>
                <tr><th>Tool</th><th>Results</th><th>Count</th></tr>
                {% for tool, result in results.items() %}
                <tr><td>{{ tool }}</td><td><pre>{{ result }}</pre></td><td>{{ result|length }}</td></tr>
                {% endfor %}
            </table>
        </div>
        {% endfor %}
        <h2>Live Hosts</h2>
        <pre>{{ live_results }}</pre>
        <h2>Non-Resolved Hosts</h2>
        <pre>{{ non_resolved_results }}</pre>
        <h2>Important Assets</h2>
        <pre>{{ important_results }}</pre>
        <h2>Secrets</h2>
        <pre>{{ secrets_results }}</pre>
        <h2>Vulnerabilities</h2>
        <pre>{{ vulns_results }}</pre>
        <h2>Sensitive Domains for Manual Review</h2>
        <pre>{{ sensitive_domains }}</pre>
    </body>
    </html>
    """
    report = {
        "Subdomain Enumeration": {},
        "Secret Finding": {},
        "Endpoint Extraction": {},
        "Vulnerability Scanning": {},
        "Cloud and IP Discovery": {}
    }
    
    for tool_output in tool_outputs:
        tool_name = os.path.basename(tool_output).split('_')[0]
        phase = "Unknown"
        if tool_name in ["subfinder", "assetfinder", "findomain", "amass", "sublist3r", "gotator", "puredns", "subdomainfinder", "crt_sh", "dnsrecon", "certspotter", "dnsgen"]:
            phase = "Subdomain Enumeration"
        elif tool_name in ["trufflehog", "gitleaks", "secretfinder", "gf", "emailhunter", "theHarvester"]:
            phase = "Secret Finding"
        elif tool_name in ["katana", "ffuf", "gau", "waybackurls"]:
            phase = "Endpoint Extraction"
        elif tool_name in ["nuclei", "zap", "metasploit"]:
            phase = "Vulnerability Scanning"
        elif tool_name in ["cloud-enum", "dnsdumpster", "shodan"]:
            phase = "Cloud and IP Discovery"
        
        try:
            with open(tool_output, 'r') as f:
                report[phase][tool_name] = f.read().splitlines()
        except Exception as e:
            ErrorHandler.log_error(f"Error reading {tool_output} for report: {e}")

    live_results = non_resolved_results = important_results = secrets_results = vulns_results = ""
    try:
        with open(live_output, 'r') as f:
            live_results = f.read()
    except Exception as e:
        ErrorHandler.log_error(f"Error reading live output: {e}")
    try:
        with open(non_resolved_output, 'r') as f:
            non_resolved_results = f.read()
    except Exception as e:
        ErrorHandler.log_error(f"Error reading non-resolved output: {e}")
    try:
        with open(important_output, 'r') as f:
            important_results = f.read()
    except Exception as e:
        ErrorHandler.log_error(f"Error reading important output: {e}")
    try:
        with open(secrets_output, 'r') as f:
            secrets_results = f.read()
    except Exception as e:
        ErrorHandler.log_error(f"Error reading secrets output: {e}")
    try:
        with open(vulns_output, 'r') as f:
            vulns_results = f.read()
    except Exception as e:
        ErrorHandler.log_error(f"Error reading vulns output: {e}")

    sensitive_domains = "\n".join([line for line in live_results.splitlines() if any(keyword in line.lower() for keyword in ["api", "admin", "test", "dev", "staging"])])

    env = jinja2.Environment()
    template = env.from_string(template)
    try:
        total_time = str(datetime.now() - datetime.strptime(list(report.values())[0][list(report.values())[0].keys()[0]][0]["start_time"], "%Y-%m-%d %H:%M:%S"))
    except:
        total_time = "Unknown"
    with open(f"output/report_{target}.html", "w") as f:
        f.write(template.render(
            target=target,
            report=report,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            live_results=live_results,
            non_resolved_results=non_resolved_results,
            important_results=important_results,
            secrets_results=secrets_results,
            vulns_results=vulns_results,
            sensitive_domains=sensitive_domains,
            total_time=total_time,
            subdomain_count=len(live_results.splitlines()) + len(non_resolved_results.splitlines()),
            secret_count=len(secrets_results.splitlines()),
            vuln_count=len(vulns_results.splitlines())
        ))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted! State saved. Run with --resume to continue.")
        sys.exit(1)
