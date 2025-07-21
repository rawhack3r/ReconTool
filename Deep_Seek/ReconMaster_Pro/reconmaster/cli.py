#!/usr/bin/env python3
import asyncio
import argparse
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from .core.orchestrator import ReconOrchestrator

console = Console()

async def run_recon(target: str, config: str):
    recon = ReconOrchestrator()
    config_path = Path(__file__).parent.parent / "configs" / f"{config}.yaml"
    
    if not await recon.load_config(config_path):
        console.print("[red]× Config load failed![/]")
        return False

    phases = {
        "passive": ("[cyan]Passive Recon[/]", "📡"),
        "active": ("[yellow]Active Scanning[/]", "🔍"), 
        "intel": ("[magenta]Intel Gathering[/]", "🧠")
    }
    
    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        console=console
    ) as progress:
        main_task = progress.add_task("[bold green]Overall Progress", total=len(phases))
        
        for phase, (desc, icon) in phases.items():
            phase_task = progress.add_task(f"{icon} {desc}", total=1)
            
            results, stats = await recon.execute_phase(phase, target)
            progress.update(phase_task, advance=1)
            
            console.print(
                f"\n{desc} RESULTS:\n"
                f"• Tools executed: [bold]{len(results)}[/]\n"
                f"• Time elapsed: [bold]{stats['time']:.2f}s[/]\n"
                f"• CPU usage: [bold]{stats['cpu']:.1f}%[/]\n"
                f"• Memory used: [bold]{stats['memory']:.1f} MB[/]"
            )
            progress.update(main_task, advance=1)
    
    recon.error_handler.report()
    return True

def main():
    parser = argparse.ArgumentParser(description="ReconMaster Pro - Automated Reconnaissance Tool")
    parser.add_argument("-t", "--target", required=True, help="Target domain or IP")
    parser.add_argument("-c", "--config", choices=["default", "deep"], default="default")
    args = parser.parse_args()
    
    if not asyncio.run(run_recon(args.target, args.config)):
        exit(1)

if __name__ == "__main__":
    main()