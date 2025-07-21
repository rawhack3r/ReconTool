from rich.panel import Panel
from rich.console import Console

console = Console()

def banner_text(target, mode):
    return f"""
[bold magenta]███ N I G H T O W L ███[/bold magenta]
[bold magenta]Made in India by n00bhack3r
With the help of Perplexity[/bold magenta]

[green bold]Target: [/] {target}    [yellow]| Mode:[/] {mode.upper()}
"""

def draw_banner(target, mode):
    console.print(Panel(banner_text(target, mode), title="🚀 NightOwl - AI Recon Master", border_style="bright_magenta"))
