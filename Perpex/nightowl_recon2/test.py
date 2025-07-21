from rich.layout import Layout
from rich.live import Live
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.box import ROUNDED, DOUBLE
from rich.table import Table
import time

console = Console()

def create_demo_panel(title, content, color="cyan", box=ROUNDED):
    return Panel(Text(content, style="bold"), title=title, border_style=color, box=box)

def build_layout_tree():
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=6)
    )

    layout["main"].split_row(
        Layout(name="left", size=20),
        Layout(name="center", ratio=2),
        Layout(name="right", size=48)
    )

    layout["left"].split_column(
        Layout(name="target", size=3),
        Layout(name="resources", size=3),
        Layout(name="phase", size=3)
    )

    layout["right"].split_column(
        Layout(name="tools", ratio=2),
        Layout(name="results", ratio=2),
        Layout(name="errors", size=8)
    )

    return layout

def update_layout(layout, tick=0):
    # HEADER
    layout["header"].update(create_demo_panel("🦉 NightOwl Header", f"Tick: {tick}", color="magenta", box=DOUBLE))

    # LEFT
    layout["left"]["target"].update(create_demo_panel("🎯 Target", "example.com"))
    layout["left"]["resources"].update(create_demo_panel("📡 Resources", "CPU: 11%\nRAM: 42%"))
    layout["left"]["phase"].update(create_demo_panel("🚦 Phase", "2 / 5"))

    # CENTER
    logs = "\n".join([f"[LIVE] sub{tick}.example.com", f"[INFO] Phase ticking..."])
    layout["center"].update(Panel(Text(logs, style="green"), title="🦾 Verbose Output", border_style="bright_cyan", box=DOUBLE))

    # RIGHT
    layout["right"]["tools"].update(create_demo_panel("🛠 Tools", "subfinder ✅\ndnsx ✅"))
    layout["right"]["results"].update(create_demo_panel("📊 Results", "240 domains"))
    layout["right"]["errors"].update(create_demo_panel("⚠ Errors", "crtsh: timeout", color="red"))

    # FOOTER
    summary = Text()
    summary.append("Completed: 2\n", style="green")
    summary.append("Failed: 1\n", style="red")
    footer_msg = Text("NightOwl Recon: FUTURE-READY. ALL SYSTEMS OPERATIONAL.", style="bold cyan")
    layout["footer"].update(Panel(Group(summary, footer_msg), box=DOUBLE, border_style="bright_cyan"))

async def main():
    layout = build_layout_tree()
    print("\n📐 Layout Tree:")
    console.print(layout.tree)  # 📋 Debug print
    tick = 0
    with Live(layout, refresh_per_second=1):
        while tick < 10:
            update_layout(layout, tick)
            tick += 1
            time.sleep(1)  # Simulate ticker update


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
