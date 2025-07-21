import argparse
import asyncio
import os
import yaml
from concurrent.futures import ThreadPoolExecutor
from core.ui import UI
from core.tools import check_tool_availability, merge_results, check_alive, grep_important
from core.report import generate_report
from core.state_manager import StateManager

def parse_args():
    parser = argparse.ArgumentParser(description="NightOwl - Automated Recon Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., swiggy.com)")
    parser.add_argument("-m", "--mode", choices=["quick", "deep"], default="quick", help="Scan mode")
    return parser.parse_args()

async def main():
    args = parse_args()
    ui = UI()
    ui.start_scan(args.target, args.mode)

    # Load config
    try:
        with open("config/config.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        ui.console.print(f"[red]Error loading config.yaml: {e}. Using default settings.[/red]")
        with open("output/errors/errors.log", "a") as f:
            f.write(f"Error loading config.yaml: {e}\n")
        config = {}

    # Initialize StateManager
    state_manager = StateManager(args.target)
    state_manager.set_mode(args.mode)

    # Start Flask dashboard
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(ui.start_dashboard)

    # Check available tools
    tools, unavailable_tools = check_tool_availability(ui, config)
    if not any(tools.values()):
        ui.console.print("[red]Error: No tools available. Please run install.sh.[/red]")
        with open("output/errors/errors.log", "a") as f:
            f.write("Error: No tools available. Please run install.sh.\n")
        return

    # Initialize result collections
    subdomains = []
    secrets = []
    endpoints = []
    vulnerabilities = []

    # Run scan phases
    enabled_subdomain_tools = [tool for tool in tools.get("subdomain_enum", []) if config.get("tools", {}).get(tool, {}).get("enabled", True)]
    total_subdomain_tools = len(enabled_subdomain_tools) or 1
    ui.console.print(f"[cyan]Enabled subdomain tools: {enabled_subdomain_tools} ({total_subdomain_tools} total)[/cyan]")

    if args.mode == "deep":
        ui.console.print("[cyan]Starting deep scan...[/cyan]")
        for i, tool in enumerate(enabled_subdomain_tools, 1):
            ui.console.print(f"[cyan]Running {tool} ({i}/{total_subdomain_tools})...[/cyan]")
            try:
                # Dynamically call the tool function
                func = globals().get(f"run_{tool}")
                if func:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = func(ui, args.target, config=config)
                    subdomains.extend(result)
                    ui.console.print(f"[cyan]{tool} found {len(result)} subdomains[/cyan]")
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                else:
                    ui.console.print(f"[red]Error: Function run_{tool} not found in core/tools.py.[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error: Function run_{tool} not found for {args.target}\n")
            except Exception as e:
                ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                with open("output/errors/errors.log", "a") as f:
                    f.write(f"Error running {tool} on {args.target}: {e}\n")
                ui.end_tool(tool, [], stderr=str(e), error=True)
            ui.update_phase_progress(tool)

        subdomains = merge_results(ui, args.target, config)
        state_manager.update_progress("phase_1_subdomain_enumeration", min(100, len(enabled_subdomain_tools) * 20))
        alive = check_alive(ui, args.target, config)
        dead = list(set(subdomains) - set(alive))
        state_manager.update_subdomains(alive)
        important = grep_important(ui, args.target, config)

        ui.console.print("[cyan]Running secret finding...[/cyan]")
        for tool in tools.get("secret_finding", []):
            if config.get("tools", {}).get(tool, {}).get("enabled", True):
                try:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = globals()[f"run_{tool}"](ui, args.target, config=config)
                    secrets.extend(result)
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                except Exception as e:
                    ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error running {tool} on {args.target}: {e}\n")
                    ui.end_tool(tool, [], stderr=str(e), error=True)
                ui.update_phase_progress(tool)
        state_manager.update_progress("phase_2_secret_finding", 100)

        ui.console.print("[cyan]Running asset identification...[/cyan]")
        for tool in tools.get("asset_discovery", []):
            if config.get("tools", {}).get(tool, {}).get("enabled", True):
                try:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = globals()[f"run_{tool}"](ui, args.target, config=config)
                    subdomains.extend(result)
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                except Exception as e:
                    ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error running {tool} on {args.target}: {e}\n")
                    ui.end_tool(tool, [], stderr=str(e), error=True)
                ui.update_phase_progress(tool)
        state_manager.update_progress("phase_3_asset_identification", 100)

        ui.console.print("[cyan]Running endpoint extraction...[/cyan]")
        for tool in tools.get("endpoint_extraction", []):
            if config.get("tools", {}).get(tool, {}).get("enabled", True):
                try:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = globals()[f"run_{tool}"](ui, args.target, config=config)
                    endpoints.extend(result)
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                except Exception as e:
                    ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error running {tool} on {args.target}: {e}\n")
                    ui.end_tool(tool, [], stderr=str(e), error=True)
                ui.update_phase_progress(tool)
        state_manager.update_progress("phase_4_endpoint_extraction", 100)

        ui.console.print("[cyan]Running vulnerability scanning...[/cyan]")
        for tool in tools.get("vulnerability_scanning", []):
            if config.get("tools", {}).get(tool, {}).get("enabled", True):
                try:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = globals()[f"run_{tool}"](ui, args.target, config=config)
                    vulnerabilities.extend(result)
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                except Exception as e:
                    ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error running {tool} on {args.target}: {e}\n")
                    ui.end_tool(tool, [], stderr=str(e), error=True)
                ui.update_phase_progress(tool)
        state_manager.update_progress("phase_5_vulnerability_scanning", 100)

    else:
        ui.console.print("[cyan]Starting quick scan...[/cyan]")
        for i, tool in enumerate(enabled_subdomain_tools[:2], 1):
            ui.console.print(f"[cyan]Running {tool} ({i}/2)...[/cyan]")
            try:
                func = globals().get(f"run_{tool}")
                if func:
                    result, stderr, duration, cpu, ram, net_sent, net_recv = func(ui, args.target, config=config)
                    subdomains.extend(result)
                    ui.end_tool(tool, result, duration, stderr, False, cpu, ram, net_sent, net_recv)
                else:
                    ui.console.print(f"[red]Error: Function run_{tool} not found.[/red]")
                    with open("output/errors/errors.log", "a") as f:
                        f.write(f"Error: Function run_{tool} not found for {args.target}\n")
            except Exception as e:
                ui.console.print(f"[red]Error running {tool}: {e}[/red]")
                with open("output/errors/errors.log", "a") as f:
                    f.write(f"Error running {tool} on {args.target}: {e}\n")
                ui.end_tool(tool, [], stderr=str(e), error=True)
            ui.update_phase_progress(tool)
        subdomains = merge_results(ui, args.target, config)
        state_manager.update_progress("phase_1_subdomain_enumeration", min(100, len(enabled_subdomain_tools[:2]) * 20))
        alive = check_alive(ui, args.target, config)
        dead = list(set(subdomains) - set(alive))
        state_manager.update_subdomains(alive)
        state_manager.update_progress("phase_2_secret_finding", 100)

    # Generate report
    ui.console.print("[green]Generating report...[/green]")
    generate_report(args.target, subdomains, alive, dead, important, secrets, endpoints, vulnerabilities, config)
    ui.console.print(f"[green]Report generated: output/reports/{args.target}_report.html[/green]")
    ui.finish_scan(args.target, unavailable_tools)

if __name__ == "__main__":
    asyncio.run(main())