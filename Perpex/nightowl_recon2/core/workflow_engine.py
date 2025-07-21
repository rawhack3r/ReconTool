# core/workflow_engine.py

from config.settings import WORKFLOW_PHASES

class Phase:
    def __init__(self, name, tools):
        self.name = name
        self.tools = tools

class WorkflowEngine:
    def __init__(self, mode):
        self.mode = mode

    def get_phases(self):
        phases_data = WORKFLOW_PHASES.get(self.mode, [])
        return [Phase(p["name"], p["tools"]) for p in phases_data]
