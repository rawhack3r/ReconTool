import subprocess
import os
import time
import yaml
import psutil
import shutil
from core.ui import UI

def check_tool_availability(ui, config):
    """Check which tools are installed and available."""
    tools = {
        "subdomain_enum": ["sublist3r", "amass", "assetfinder", "findomain", "subfinder", "crt_sh", "subbrute"],
        "secret_finding": ["trufflehog", "gitleaks", "hunter_io", "github_scanner"],
        "asset_discovery": ["dnsx", "gotator", "puredns", "whois", "cloud_scanner", "hakip2host"],
        "endpoint_extraction": ["katana", "ffuf", "waybackurls", "jsa"],
        "vulnerability_scanning": ["nuclei", "zap", "subjack"]
    }
    available_tools = {}
    unavailable_tools = []
    for category, tool_list in tools.items():
        available_tools[category] = []
        for tool in tool_list:
            if not config.get("tools", {}).get(tool, {}).get("enabled", True):
                ui.console.print(f"[yellow]Skipping {tool} (disabled in config).[/yellow]")
                continue
            if tool in ["crt_sh", "subbrute", "hunter_io", "github_scanner", "jsa"]:
                if os.path.exists(f"tools/{'subdomain_enum' if tool in ['crt_sh', 'subbrute'] else 'osint' if tool in ['hunter_io', 'github_scanner'] else 'endpoint_extraction'}/{tool}.py"):
                    available_tools[category].append(tool)
                else:
                    unavailable_tools.append(tool)
                    ui.console.print(f"[yellow]Warning: {tool}.py not found in tools/ directory.[/yellow]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Warning: {tool}.py not found in tools/ directory for {category}\n")
            else:
                if shutil.which(tool):
                    available_tools[category].append(tool)
                    ui.console.print(f"[cyan]Tool {tool} is available.[/cyan]")
                else:
                    unavailable_tools.append(tool)
                    ui.console.print(f"[red]Warning: {tool} not installed or not found in PATH.[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Warning: {tool} not installed or not found in PATH for {category}\n")
    return available_tools, unavailable_tools

def run_sublist3r(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/sublist3r.txt"
    cmd = ["sublist3r", "-d", target, "-o", output_file, "-n"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("sublist3r", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip() and not line.startswith("[-]")]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: sublist3r output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("sublist3r", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"sublist3r on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("sublist3r", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running sublist3r on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_amass(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/amass.txt"
    api_key = config.get("tools", {}).get("amass", {}).get("api_key", "") if config else ""
    cmd = ["amass", "enum", "-d", target, "-o", output_file, "-passive"]
    if api_key:
        cmd.extend(["-config", api_key])
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("amass", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: amass output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("amass", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"amass on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("amass", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running amass on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_assetfinder(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/assetfinder.txt"
    cmd = ["assetfinder", "--subs-only", target]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("assetfinder", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = [line.strip() for line in result.stdout.splitlines() if line.strip() and target in line]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        if not results:
            ui.console.print(f"[red]Warning: No valid subdomains found by assetfinder for {target}.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: assetfinder found no valid subdomains for {target}\n")
        ui.end_tool("assetfinder", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"assetfinder on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("assetfinder", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running assetfinder on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_findomain(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/findomain.txt"
    cmd = ["findomain", "-t", target, "-u", output_file, "--quiet"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("findomain", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: findomain output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("findomain", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"findomain on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("findomain", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running findomain on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_subfinder(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/subfinder.txt"
    cmd = ["subfinder", "-d", target, "-o", output_file, "-silent", "-all"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("subfinder", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: subfinder output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("subfinder", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"subfinder on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("subfinder", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running subfinder on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_dnsx(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/dnsx.txt"
    cmd = ["dnsx", "-l", f"{output_dir}/final_subdomains.txt", "-o", output_file, "-silent"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("dnsx", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: dnsx output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("dnsx", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"dnsx on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("dnsx", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running dnsx on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_gotator(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/gotator.txt"
    cmd = ["gotator", "-s", f"{output_dir}/final_subdomains.txt", "-o", output_file, "-silent"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("gotator", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: gotator output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("gotator", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"gotator on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("gotator", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running gotator on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_puredns(ui, target, output_dir="output/subdomains", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/puredns.txt"
    cmd = ["puredns", "resolve", f"{output_dir}/final_subdomains.txt", "-w", output_file, "--resolvers", config["general"]["resolver_file"]] if config and config.get("general", {}).get("resolver_file") else ["puredns", "resolve", f"{output_dir}/final_subdomains.txt", "-w", output_file]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("puredns", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: puredns output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("puredns", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"puredns on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("puredns", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running puredns on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_trufflehog(ui, target, output_dir="output/important/secret", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/trufflehog.txt"
    cmd = ["trufflehog", "git", f"https://{target}", "--regex", "--entropy=True", "--json"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("trufflehog", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        if not results:
            ui.console.print(f"[red]Warning: No secrets found by trufflehog for {target}.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: trufflehog found no secrets for {target}\n")
        ui.end_tool("trufflehog", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"trufflehog on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("trufflehog", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running trufflehog on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_katana(ui, target, output_dir="output/important/endpoints", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/katana.txt"
    cmd = ["katana", "-u", f"https://{target}", "-o", output_file, "-silent"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("katana", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: katana output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("katana", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"katana on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("katana", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running katana on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_ffuf(ui, target, output_dir="output/important/endpoints", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/ffuf.json"
    cmd = ["ffuf", "-u", f"https://{target}/FUZZ", "-w", config["general"]["wordlist_dir"] + "/directories.txt", "-o", output_file, "-silent", "-of", "json"] if config and config.get("general", {}).get("wordlist_dir") else ["ffuf", "-u", f"https://{target}/FUZZ", "-w", "data/wordlists/directories.txt", "-o", output_file, "-silent", "-of", "json"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("ffuf", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                import json
                data = json.load(f)
                results = [item["url"] for item in data.get("results", [])]
            with open(f"{output_dir}/ffuf.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: ffuf output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("ffuf", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"ffuf on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("ffuf", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running ffuf on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_waybackurls(ui, target, output_dir="output/important/endpoints", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/waybackurls.txt"
    cmd = ["waybackurls", target]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("waybackurls", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(results))
        if not results:
            ui.console.print(f"[red]Warning: No endpoints found by waybackurls for {target}.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: waybackurls found no endpoints for {target}\n")
        ui.end_tool("waybackurls", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"waybackurls on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("waybackurls", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running waybackurls on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_nuclei(ui, target, output_dir="output/vulnerabilities", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/vuln_nuclei.json"
    cmd = ["nuclei", "-u", target, "-t", config["tools"]["nuclei"]["template_dir"], "-o", output_file, "-silent", "-json"] if config and config.get("tools", {}).get("nuclei", {}).get("template_dir") else ["nuclei", "-u", target, "-t", "data/nuclei_templates", "-o", output_file, "-silent", "-json"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("nuclei", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                import json
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        results.append(f"{data.get('info', {}).get('name', 'Unknown')}: {data.get('host', '')}")
            with open(f"{output_dir}/vuln_nuclei.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: nuclei output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("nuclei", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"nuclei on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("nuclei", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running nuclei on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def run_subjack(ui, target, output_dir="output/vulnerabilities", config=None):
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/vuln_subjack.txt"
    cmd = ["subjack", "-w", f"{output_dir}/../subdomains/final_subdomains.txt", "-o", output_file, "-silent"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("subjack", target)
    try:
        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        results = []
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                results = [line.strip() for line in f if line.strip()]
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: subjack output file {output_file} is empty or not created for {target}\n")
        ui.end_tool("subjack", results, duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"subjack on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return results, result.stderr, duration, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024
    except Exception as e:
        ui.end_tool("subjack", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running subjack on {target}: {e}\n")
        return [], str(e), 0, 0, 0, 0, 0

def merge_results(ui, target, config):
    """Merge results from multiple tools."""
    subdomains = set()
    output_dir = config.get("general", {}).get("output_dir", "output") if config else "output"
    subdomain_dir = f"{output_dir}/subdomains"
    os.makedirs(subdomain_dir, exist_ok=True)
    ui.console.print(f"[cyan]Merging subdomains from {subdomain_dir}...[/cyan]")
    for file in os.listdir(subdomain_dir):
        file_path = os.path.join(subdomain_dir, file)
        if file.endswith(".txt") and file not in ["final_subdomains.txt", "alive.txt", "dead.txt"]:
            ui.console.print(f"[cyan]Processing {file_path}...[/cyan]")
            try:
                if os.path.getsize(file_path) > 0:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and target in line and not line.startswith("[-]"):
                                subdomains.add(line)
                else:
                    ui.console.print(f"[red]Warning: {file_path} is empty.[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Warning: {file_path} is empty for {target}\n")
            except Exception as e:
                ui.console.print(f"[red]Error reading {file_path}: {e}[/red]")
                with open("output/errors/errors.log", "a") as f:
                    f.write(f"Error reading {file_path}: {e}\n")
    final_output = f"{subdomain_dir}/final_subdomains.txt"
    with open(final_output, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(subdomains)))
    ui.console.print(f"[cyan]Merged {len(subdomains)} subdomains into {final_output}[/cyan]")
    return list(subdomains)

def check_alive(ui, target, config):
    """Check which subdomains are alive using httpx."""
    output_dir = config.get("general", {}).get("output_dir", "output") if config else "output"
    input_file = f"{output_dir}/subdomains/final_subdomains.txt"
    output_file = f"{output_dir}/subdomains/alive.txt"
    cmd = ["httpx", "-l", input_file, "-o", output_file, "-silent", "-status-code", "-no-fallback", "-timeout", "15", "-threads", "100", "-http2"]
    process = psutil.Process()
    start_time = time.time()
    ui.start_tool("httpx", target)
    try:
        if not os.path.exists(input_file):
            ui.console.print(f"[red]Error: {input_file} does not exist.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Error: httpx input file {input_file} does not exist for {target}\n")
            ui.end_tool("httpx", [], 0, "Input file does not exist", True, 0, 0, 0, 0)
            return []
        if os.path.getsize(input_file) == 0:
            ui.console.print(f"[red]Error: {input_file} is empty.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Error: httpx input file {input_file} is empty for {target}\n")
            ui.end_tool("httpx", [], 0, "Input file empty", True, 0, 0, 0, 0)
            return []

        ui.console.print(f"[cyan]Executing: {' '.join(cmd)}[/cyan]")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        cpu = process.cpu_percent()
        ram = process.memory_percent()
        net = psutil.net_io_counters()
        subdomains = set()
        with open(input_file, "r", encoding="utf-8") as f:
            subdomains = set(line.strip() for line in f if line.strip())

        alive = set()
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and ("[200]" in line or "[301]" in line or "[302]" in line):
                        subdomain = line.split()[0].replace("http://", "").replace("https://", "").strip()
                        if subdomain:
                            alive.add(subdomain)
        else:
            ui.console.print(f"[red]Warning: {output_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: httpx output file {output_file} is empty or not created for {target}\n")

        dead = subdomains - alive
        dead_file = f"{output_dir}/subdomains/dead.txt"
        with open(dead_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(dead)))
        ui.end_tool("httpx", list(alive), duration, result.stderr, False, cpu, ram, net.bytes_sent / 1024, net.bytes_recv / 1024)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"httpx on {target}: stdout={result.stdout}, stderr={result.stderr}\n")
        return list(alive)
    except Exception as e:
        ui.end_tool("httpx", [], stderr=str(e), error=True)
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error running httpx on {target}: {e}\n")
        return []

def grep_important(ui, target, config):
    """Filter important subdomains or endpoints."""
    output_dir = config.get("general", {}).get("output_dir", "output") if config else "output"
    try:
        with open("config/patterns.yaml", "r", encoding="utf-8") as f:
            patterns = yaml.safe_load(f)
        subdomains = set()
        input_file = f"{output_dir}/subdomains/final_subdomains.txt"
        if os.path.exists(input_file) and os.path.getsize(input_file) > 0:
            with open(input_file, "r", encoding="utf-8") as f:
                subdomains = set(line.strip() for line in f if line.strip())
        else:
            ui.console.print(f"[red]Warning: {input_file} is empty or not created.[/red]")
            with open("output/errors/errors.log", "a") as f:
                f.write(f"Warning: grep_important input file {input_file} is empty or not created for {target}\n")
        important = [d for d in subdomains if any(p in d.lower() for p in patterns.get("sensitive_path", "").split("|"))]
        output_file = f"{output_dir}/important/important.txt"
        os.makedirs(f"{output_dir}/important", exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(important)))
        ui.console.print(f"[cyan]Found {len(important)} important subdomains[/cyan]")
        return important
    except Exception as e:
        ui.console.print(f"[red]Error in grep_important: {e}[/red]")
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error in grep_important for {target}: {e}\n")
        return []