from rich.panel import Panel
from rich.console import Console

console = Console()

def banner_text(target, mode):
    return f"""
[bold magenta]██████  ███████  ██████   ██████  ███    ██ ██████  ███████ ████████ ██      ██      ██████  ███████ [/bold magenta]
[bold magenta]██╔══██ ██╔════╝██╔═══██ ██    ██ ████   ██ ██╔══██ ██╔════╝   ██    ██      ██     ██       ██╔════╝[/bold magenta]
[bold magenta]██████╔╝█████   ██    ██ ██    ██ ██ ██  ██ ██   ██ ███████    ██    ██      ██     ██   ███ ███████ [/bold magenta]
[bold magenta]██╔═══╝ ██╔══╝  ██    ██ ██    ██ ██  ██ ██ ██   ██ ╚════██    ██    ██      ██     ██    ██ ╚════██ [/bold magenta]
[bold magenta]██      ███████ ╚██████╔╝╚██████╔╝██   ████ ██████  ███████    ██    ███████ ███████ ╚██████╔╝███████ [/bold magenta]

[green bold]Target: [/] {target}    [yellow]| Mode:[/] {mode.upper()}
"""

def draw_banner(target, mode):
    console.print(Panel(banner_text(target, mode), title="🚀 ReconStellr - Powered by n00bh4ck3r.ai", border_style="bright_magenta"))
