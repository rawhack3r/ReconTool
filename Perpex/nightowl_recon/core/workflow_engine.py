from config.settings import WORKFLOW_PHASES

class Phase:
    def __init__(self, name, tools, description="", parallel=True):
        self.name = name
        self.tools = tools
        self.description = description
        self.parallel = parallel

class WorkflowEngine:
    def __init__(self, mode, custom_tools=None):
        self.mode = mode
        self.custom_tools = custom_tools

    def get_phases(self):
        if self.mode == "custom" and self.custom_tools:
            return [
                Phase(name="Custom Tools", tools=self.custom_tools, description="User-specified tools", parallel=False)
            ]
        phases = []
        for raw in WORKFLOW_PHASES.get(self.mode, []):
            phases.append(Phase(name=raw["name"], tools=raw["tools"], description=raw["description"], parallel=raw.get("parallel", True)))
        return phases
