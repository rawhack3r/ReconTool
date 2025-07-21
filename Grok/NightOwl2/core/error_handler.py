
import logging
import os

class ErrorHandler:
    def __init__(self):
        os.makedirs("output/errors", exist_ok=True)
        logging.basicConfig(filename='output/errors/errors.log', level=logging.ERROR, format='%(asctime)s - %(message)s')
        self.failed_tools = {}

    def log_error(self, tool, target, error):
        logging.error(f"{tool} on {target}: {error}")
        if target not in self.failed_tools:
            self.failed_tools[target] = []
        self.failed_tools[target].append(tool)

    def relaunch_failed_tools(self, target, ui, state_manager, config):
        if target in self.failed_tools:
            ui.console.print(f"[yellow]Relaunching failed tools for {target}...[/yellow]")
            for tool in self.failed_tools[target]:
                ui.start_tool(tool, target)
                try:
                    results, stderr, duration, cpu, ram, net_sent, net_recv = globals()[f"run_{tool}"](target, config=config)
                    ui.end_tool(tool, results, duration, stderr, cpu, ram, net_sent, net_recv)
                    state_manager.update_state(target, tool, "completed")
                except Exception as e:
                    self.log_error(tool, target, str(e))
                    ui.end_tool(tool, None, duration=None, error=True, stderr=str(e))
            self.failed_tools[target] = []