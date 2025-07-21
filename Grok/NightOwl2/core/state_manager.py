import json
import os

class StateManager:
    def __init__(self, target=""):
        self.state_file = "output/state.json"
        self.state = {
            "target": target,
            "mode": "",
            "subdomains": [],
            "progress": {
                "phase_1_subdomain_enumeration": 0,
                "phase_2_secret_finding": 0,
                "phase_3_asset_identification": 0,
                "phase_4_endpoint_extraction": 0,
                "phase_5_vulnerability_scanning": 0
            },
            "current_tools": {}
        }
        self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r", encoding="utf-8") as f:
                self.state.update(json.load(f))

    def save_state(self):
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=4)

    def set_target(self, target):
        self.state["target"] = target
        self.save_state()

    def set_mode(self, mode):
        self.state["mode"] = mode
        self.save_state()

    def get_target(self):
        return self.state.get("target", "")

    def get_mode(self):
        return self.state.get("mode", "")

    def get_progress(self):
        return self.state.get("progress", {})

    def update_progress(self, phase, value):
        if phase in self.state["progress"]:
            self.state["progress"][phase] = min(100, max(0, value))
            self.save_state()

    def update_subdomains(self, subdomains):
        self.state["subdomains"].extend(subdomains)
        self.save_state()

    def update_tool_status(self, tool, status):
        self.state["current_tools"][tool] = status
        self.save_state()

    def get_tool_status(self, tool):
        return self.state["current_tools"].get(tool, "Not Started")

    def get_state(self):
        return self.state
