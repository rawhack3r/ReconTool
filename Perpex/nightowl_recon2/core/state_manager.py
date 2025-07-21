import json
from pathlib import Path

class StateManager:
    def __init__(self, output_dir):
        self.state_path = Path(output_dir) / "state.json"

    def save_state(self, state):
        with open(self.state_path, "w") as f:
            json.dump(state, f, indent=2)

    def load_state(self):
        if self.state_path.exists():
            with open(self.state_path) as f:
                return json.load(f)
        return {}
