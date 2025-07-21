from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime

console = Console()

def show_final_summary(completion_log, errors, output_dir, stats=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    table = Table(title="📊 Final Scan Status", show_lines=True)
    table.add_column("Phase")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Results")

    for tup in stats or []:
        phase, tool, status, count = tup
        icon = "✅" if status == "completed" else "❌"
        table.add_row(phase, tool, icon, str(count))

    panel = Panel.fit(f"""
[bold]Finished at:[/bold] {timestamp}
[green]Passed:[/green] {list(completion_log.values()).count('completed')}
[red]Failed:[/red] {len(errors)}
[cyan]Output directory:[/cyan] {output_dir}
    """, title="Summary", border_style="bold green")
    console.print(table)
    console.print(panel)
